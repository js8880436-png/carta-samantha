[app]

# (str) Título do aplicativo
title = Carta Samantha

# (str) Nome do pacote (ex: org.minhaapp.meuapp)
package.name = cartasamantha

# (str) Domínio do pacote (ex: org.minhaapp)
package.domain = org.js8880436

# (str) Versão do código fonte
version = 1.0.0

# (list) Requisitos (bibliotecas Python)
requirements = python3,kivy,android

# (str) Arquivo principal do aplicativo
source.dir = .

# (list) Extensões de arquivo a incluir
source.include_exts = py,png,jpg,kv,atlas,ttf

# (list) Arquivos/pastas a incluir (ex: imagens, fontes)
# Como as mídias estão na pasta do celular, não precisam estar no APK
# Mas se você tiver imagens estáticas, coloque aqui.

# (str) Ícone do aplicativo
icon.filename = %(source.dir)s/icon.png

# (str) Presplash (tela de abertura)
presplash.filename = %(source.dir)s/presplash.png

# (list) Permissões Android
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (int) API mínima do Android
android.api = 30

# (int) API alvo
android.target_sdk = 34

# (str) NDK a ser usado (deixe vazio para o Buildozer escolher)
android.ndk = 

# (bool) Usar o SDK do sistema (se disponível)
android.sdk_path = 

# (list) Pacotes extras (ex: openssl)
android.add_src = 

# (bool) Ativar modo de depuração
android.debug = 1

[buildozer]

# (int) Nível de log (0=erro, 1=info, 2=debug)
log_level = 2

# (bool) Atualizar dependências automaticamente
warn_on_root = 1
