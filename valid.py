
schema = {
      "$jsonSchema": {
          "bsonType": "object",
          "required": [ "username", "password", "email", "role"],
          "properties": {
            "username": {
               "bsonType": "string",
               "description": "must be a string and is required",
               "minLength": 3,
               "maxLength": 20
            },
            "password": {
               "bsonType": "string",
               "description": "must be a string and is required",
               "minLength": 5,
               "maxLength": 25,
               "pattern"  : "^[0-9][A-Z][a-z]$"
            },
            "email": {
               "bsonType": "string",
               "description": "must be a string and is required",
               "minLength": 5,
               "maxLength": 35
            },
            "role": {
               "bsonType": "int",
               "description": "must be a number and is required",
               "minimum": 0,
               "maximum": 1
            },
            "course": {
                "bsonType": "array",
                "description": "must be array and not required"
            }
          }
      }
    }


