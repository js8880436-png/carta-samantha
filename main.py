from android.permissions import request_permissions, Permission

# Dentro do método build() da classe App, ou no início do código:
request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
