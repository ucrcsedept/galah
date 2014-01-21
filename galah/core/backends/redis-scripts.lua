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
