class InternalServerError(Exception):
    pass

class SchemaValidationError(Exception):
    pass

class ContentAlreadyExistsError(Exception):
    pass

class UpdatingContentError(Exception):
    pass

class DeletingContentError(Exception):
    pass

class ContentNotExistsError(Exception):
    pass

class EmailAlreadyExistsError(Exception):
    pass

class UnauthorizedError(Exception):
    pass

errors = {
    "InternalServerError": {
        "message": "Something went wrong",
        "status": 500
    },
     "SchemaValidationError": {
         "message": "Request is missing required fields",
         "status": 400
     },
     "ContentAlreadyExistsError": {
         "message": "Content with given name already exists",
         "status": 400
     },
     "UpdatingContentError": {
         "message": "Updating Content added by other is forbidden",
         "status": 403
     },
     "DeletingContentError": {
         "message": "Deleting Content added by other is forbidden",
         "status": 403
     },
     "ContentNotExistsError": {
         "message": "Content with given id doesn't exists",
         "status": 400
     }
}