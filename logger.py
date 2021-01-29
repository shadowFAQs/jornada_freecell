def init_log():
    open('log.txt', 'w+').close()

def log(fn_name, string):
    with open('log.txt') as file:
        lines = sorted(file.read().split('\n'), reverse=True)

    with open('log.txt', 'a') as file:
        fn_lines = [l for l in lines if 'fn [' in l]
        if fn_lines:
            most_recent_fn_name = fn_lines[0].replace('fn [', '').replace(']', '')
            if most_recent_fn_name == fn_name:
                file.write(f'\n\t{string}')
            else:
                file.write(f'\n\nfn [{fn_name}]\n\t{string}')
        else:
            file.write(f'\n\nfn [{fn_name}]\n\t{string}')
