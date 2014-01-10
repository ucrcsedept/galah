----script vmfactory_grab:check_dirty

local dirty_vm_id = redis.call("rpop", KEYS[1])
if dirty_vm_id == false then
    return false
end

-- Get and decode the vmfactory object
local vmfactory_json = redis.call("hget", KEYS[2], ARGV[1])
if vmfactory_json == false then
    return -1
end
local vmfactory = cjson.decode(vmfactory_json)

-- Set the currently_destroying key and persist the change
vmfactory["currently_destroying"] = dirty_vm_id
redis.call("hset", KEYS[2], ARGV[1], cjson.encode(vmfactory))

return dirty_vm_id

----script vmfactory_grab:check_clean

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
