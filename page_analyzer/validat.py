import validators


def valid(url):
    errors = {}
    if len(url) > 255:
        errors['big_len'] = 'Url привышает размер 255 символов'
    if not validators.url(url):
        errors['valid'] = 'Введите корректный url'
    if not url:
        errors['empty'] = 'url не должен быть пустой'
    return errors
