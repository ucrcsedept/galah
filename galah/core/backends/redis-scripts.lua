----script vmfactory_note_clean_id:note
-- keys = (vmfactory_nodes), args = (vmfactory_id, clean_id)
-- Returns 1 on success, -1 if the vmfactory was not registered, -2 if it was
--     not creating a VM, or -3 if the vmfactory already named its vm

-- Get and decode the vmfactory object
local vmfactory_json = redis.call("hget", KEYS[1], ARGV[1])
if vmfactory_json == false then
    return -1
end
local vmfactory = cjson.decode(vmfactory_json)

if vmfactory["currently_creating"] == cjson.null then
    return -2
elseif vmfactory["currently_creating"] ~= "" then
    return -3
end

vmfactory["currently_creating"] = ARGV[2]
redis.call("hset", KEYS[1], ARGV[1], cjson.encode(vmfactory))

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
if vmfactory["currently_destroying"] ~= cjson.null then
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
    if vmfactory["currently_creating"] ~= cjson.null then
        return -2
    end

    -- Set the currently_creating key and persist the change. Note the
    -- empty string is a placeholder signifying that the ID has not yet been
    -- determined.
    vmfactory["currently_creating"] = ""
    redis.call("hset", KEYS[2], ARGV[1], cjson.encode(vmfactory))

    return 1
end

return 0
