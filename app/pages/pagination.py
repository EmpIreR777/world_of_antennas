def paginate(total_items: int, page: int = 1, page_size: int = 10):
    """
    Вычисляет параметры пагинации.

    :param total_items: Общее количество элементов.
    :param page: Номер текущей страницы.
    :param page_size: Количество элементов на странице.
    :return: Словарь с параметрами пагинации: offset, limit, total_pages.
    """
    if total_items is None or total_items < 0:
        total_items = 0

    # Вычисляем общее количество страниц
    total_pages = (total_items + page_size - 1) // page_size

    # Вычисляем смещение (offset) и лимит (limit)
    offset = (page - 1) * page_size
    limit = page_size

    return {
        "offset": offset,
        "limit": limit,
        "total_pages": total_pages,
    }