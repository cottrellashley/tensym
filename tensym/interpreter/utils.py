from typing import List, Any, TypeVar, Optional

T = TypeVar('T')

def custom_list_index_getter(_list: List, _value: Any) -> int:
    """
    Return the index of the first occurrence of _value in _list.
    If _value is not in the list, return -1.
    :param _list: The list to search in.
    :param _value: the value to search for.
    :return: int index of the first occurrence of _value in _list.
    """
    try:
        return _list.index(_value)
    except ValueError:
        return -1

def get_position(__value: T, __list: List[T]) -> Optional[int]:
    """
    Gets the index of the value within the list. If value not in list, returns None.
    :param __value: The value to look for the index within list.
    :param __list: The list to look for the value.
    :return: Optional int.
    """
    try:
        return __list.index(__value)
    except ValueError as e:
        return None
