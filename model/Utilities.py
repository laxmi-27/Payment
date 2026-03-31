from flask import flash, jsonify, json
from enum import Enum

class ItemCRUDType(Enum):
    Village = 1
    Block = 2
    District = 3
    State = 4
    HoldType = 5
    Subcontractor = 6
    GSTRelease = 7

class RegEx:
    patternAlphabetOnly = r"^[A-Za-z ]+$"
    allPattern = r"^(?!\s*$).+"


class ResponseHandler:
    @staticmethod
    def invalid_name(entity):
        return {'status': 'error', 'message': f'Invalid {entity} name. Only letters are allowed!'}

    @staticmethod
    def already_exists(entity):
        return {'status': 'exists', 'message': f'{entity.capitalize()} already exists!'}

    @staticmethod
    def add_success(entity):
        return {'status': 'success', 'message': f'{entity.capitalize()} added successfully!'}

    @staticmethod
    def add_failure(entity):
        return {'status': 'error', 'message': f'Failed to add {entity}.'}

    @staticmethod
    def is_available(entity):
        return {'status': 'available', 'message': f'{entity.capitalize()} name is available!'}

    @staticmethod
    def delete_success(entity):
        return {'status': 'success', 'message': f'{entity.capitalize()} deleted successfully!'}

    @staticmethod
    def delete_failure(entity):
        return {'status': 'error', 'message': f'Failed to delete {entity}.'}

    @staticmethod
    def update_success(entity):
        return {'status': 'success', 'message': f'{entity.capitalize()} updated successfully!'}

    @staticmethod
    def update_failure(entity):
        return {'status': 'error', 'message': f'Failed to update {entity}.'}

    @staticmethod
    def fetch_failure(entity):
        return {'status': 'error', 'message': f'Failed to fetch {entity}.'}


class HtmlHelper:
    # Helper: JSON Response Formatter
    
    @staticmethod
    def json_response(message_obj, status_code):
        return jsonify(message_obj), status_code
  

