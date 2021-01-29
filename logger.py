def log(fn_name, string):
    with open('log.txt', 'a+') as file:
        file.write(f'\n{fn_name}: {string}')
