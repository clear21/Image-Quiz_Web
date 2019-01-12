from django import template

register = template.Library()

@register.filter
def file_of_one_level_folder(value):
    #カレントが xxx/yyy/ で　変数名が zzz の場合　、　xxx/zzz を返す
    return '../' + str(value) + '/'

@register.filter
def str_join_as_val_mae(value , value2):
    # a|str_join_as_val_ato:"b"   ⇒  [aの値]b ([aの値]を前にして文字結合)
    return str(value) + str(value2)

@register.filter
def str_join_as_val_ato(value , value2):
    # a|str_join_as_val_ato:"b"   ⇒  b[aの値] (bを前にして文字結合)
    return str(value2) + str(value)

#register.filter('file_of_one_level_folder', file_of_one_level_folder)