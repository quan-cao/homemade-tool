def merge_var(var1, var2):
    if var1 == '' and var2 == '':
        var = ''
    elif var1 != '' and var2 != '':
        var = var1 + ', ' + var2
    elif var1 != '' and var2 == '':
        var = var1
    else:
        var = var2
    return var