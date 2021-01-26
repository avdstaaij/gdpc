
```
PUT /blocks                     bulk update blocks (locations and block ids are in a json structure)
GET /blocks                     future feature make sense if you specify with query params

GET /blocks?x=...&y=...&z=...   get block at x, y, z
PUT /blocks?x=...&y=...&z=...   set block at x, y, z

blocks query params:

int   x, y, z               postision
int   sx, sy, sz            size
bool  includeState          if state should be included

headers: 
Accept: application/json    json support

get block (include state)
{
    blockID: "minecraft:...",
    ... state properties
}

get block (dont include state)
{
    blockID: "..."
}

get multipe blocks
{
    blocks: [{
        x: ...
        y: ...
        z: ...
        blockID: ...
        ...state properties
    }, {
        x: ...
        y: ...
        z: ...
        blockID: ...
        ...state properties
    }, {
        x: ...
        y: ...
        z: ...
        blockID: ...
        ...state properties
    }]
}

POST /blocks                    Error: by convention would add a new block (but where? :p)
POST /blocks/<x> <y> <z>        Error: shouldn't use post for update, actually
DELETE and PATCH also throw errors
```