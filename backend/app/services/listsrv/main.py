import subprocess


def list_srv(str_to_list: str, server: str):
    """
    Делает ls -lh на удалённом сервере по ssh
    :param str_to_list: команда для ls (обычно маска)
    :param server: Адрес сервера для ssh
    :return: Список словарей (из размера и путей к файлам)
    """

    args = [
        'ssh',
        server,
        'ls -lh',
        str_to_list
    ]

    cp = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    result = []

    for line in cp.stdout.splitlines():
        if line.startswith('-rw-r'):
            data = line.split()
            result.append({'size': data[4], 'name': data[-1]})

    return result
