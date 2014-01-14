----script vmfactory_unregister:unregister
-- keys = (vmfactory_nodes, dirty_vms_queue), args = (vmfactory_id)
-- Returns 0 if the vmfactory wasn't registered, -1 if the vmfactory is

-- Get and decode the vmfactory object
local vmfactory_json = redis.call("hget", KEYS[1], ARGV[1])
if vmfactory_json == false then
    -- The vmfactory wasn't registered, nothing to do
    return 0
end
local vmfactory = cjson.decode(vmfactory_json)

-- Both of these fields should not have a value (one or the other should). If
-- both of them do something weird is going on.
if (vmfactory["currently_creating"] ~= "" and
        vmfactory["currently_destroying"] ~= "") then
    return -1
end

-- If we were in the middle of creating a VM but there was no ID associated
-- with it yet we won't be able to properly clean the machine. Not sure what
-- the best course of action will be in this case.
if vmfactory["currently_creating"] == "ID_NOT_DETERMINED" then
    redis.call("hdel", "vmfactory_nodes", ARGV[1])
    return -2
end

-- If we were creating or destroying a VM, make note so we can add it to the
-- queue of dirty vms.
local recovered_vm = nil
if vmfactory["currently_creating"] ~= "" then
    recovered_vm = vmfactory["currently_creating"]
elseif vmfactory["currently_destroying"] ~= "" then
    recovered_vm = vmfactory["currently_destroying"]
end

-- Add the VM to the dirty queue (we don't need to decrement the clean VM
-- count in either case).
if recovered_vm ~= nil then
    redis.call("lpush", KEYS[2], recovered_vm)
end

-- Actually delete the vmfactory from Redis

return 1

----script vmfactory_grab:check_dirty
-- keys = (dirty_vms_queue, vmfactory_nodes), args = (vmfactory_id)
-- returns -1 if the vmfactory isn't registered, -2 if the vmfactory
--     is already destroying a vm, "" if no vm needs destroying, or
--     a UTF-8 encoded string containing the serialized VirtualMachineID
--     of the vm that needs destroying.

local dirty_vm_id = redis.call("rpop", KEYS[1])
if dirty_vm_id == false then
    return ""
end

-- Get and decode the vmfactory object
local vmfactory_json = redis.call("hget", KEYS[2], ARGV[1])
if vmfactory_json == false then
    return -1
end
local vmfactory = cjson.decode(vmfactory_json)

-- Make sure we're not in the middle of destroying a VM already
if vmfactory["currently_destroying"] ~= "" then
    return -2
end

-- Set the currently_destroying key and persist the change
vmfactory["currently_destroying"] = dirty_vm_id
redis.call("hset", KEYS[2], ARGV[1], cjson.encode(vmfactory))

return dirty_vm_id

----script vmfactory_grab:check_clean
-- keys = (dirty_vms_queue, vmfactory_nodes)
-- args = (vmfactory_id, num_desired_clean_vms)
-- returns -1 if vmfactory isn't registered, -2 if vmfactory is already
--     creating a new vm, 0 if no clean vm is needed, 1 if the vmfactory
--     should create a new vm now

local clean_vms_count = redis.call("get", KEYS[1])
if (clean_vms_count == false or
        tonumber(clean_vms_count) < tonumber(ARGV[2])) then
    -- Get and decode the vmfactory object
    local vmfactory_json = redis.call("hget", KEYS[2], ARGV[1])
    if vmfactory_json == false then
        return -1
    end
    local vmfactory = cjson.decode(vmfactory_json)

    -- Make sure we're not in the middle of creating a VM already
    if vmfactory["currently_creating"] ~= "" then
        return -2
    end

    -- Set the currently_creating key and persist the change
    vmfactory["currently_creating"] = "ID_NOT_DETERMINED"
    redis.call("hset", KEYS[2], ARGV[1], cjson.encode(vmfactory))

    return 1
end

return 0
