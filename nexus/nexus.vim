" Vim syntax file
" Language: Nexus
" Maintainer: Rafael Aires (Sunshine Studio)
" Latest Revision: 09 january 2026

if exists("b:current_syntax")
  finish
endif

" -------------------------
" Palavras-chave / Estrutura
" -------------------------
syntax keyword nexusKeyword var vet del
syntax keyword nexusKeyword se senao senaose
syntax keyword nexusKeyword funcao
syntax keyword nexusKeyword por enquanto
syntax keyword nexusKeyword escreva ler
syntax keyword nexusKeyword de para tamanho
syntax keyword nexusKeyword verdadeiro falso
syntax keyword nexusKeyword nulo

" -------------------------
" Booleanos
" -------------------------
syntax keyword nexusBoolean verdadeiro falso

" -------------------------
" Nulo
" -------------------------
syntax keyword nexusNull nulo

" -------------------------
" Operadores matemáticos e lógicos
" -------------------------
syntax match nexusOperator "="
syntax match nexusOperator "+"
syntax match nexusOperator "-"
syntax match nexusOperator "/"
syntax match nexusOperator "\*"

syntax match nexusOperator "=="
syntax match nexusOperator "!="
syntax match nexusOperator ">="
syntax match nexusOperator "<="
syntax match nexusOperator ">"
syntax match nexusOperator "<"

syntax match nexusOperator "&&"
syntax match nexusOperator "||"
syntax match nexusOperator "!"

" -------------------------
" Conversões e operadores extras textuais
" -------------------------
syntax keyword nexusConv texto inteiro tamanho

" -------------------------
" Pontuações
" -------------------------
syntax match nexusPunct "[,;:\.\?]"

" -------------------------
" Grupos
" -------------------------
syntax match nexusGroup "[()\[\]{}]"

" -------------------------
" Números
" -------------------------
syntax match nexusNumber "\<[0-9]\+\>"
syntax match nexusFloat "\<[0-9]\+\.[0-9]\+\>"

" -------------------------
" Strings
" -------------------------
syntax region nexusString start=/"/ skip=/\\"/ end=/"/
syntax region nexusString start=/'/ skip=/\\'/ end=/'/

" -------------------------
" Comentários
" -------------------------
syntax match nexusComment "//.*$"
syntax region nexusComment start="/\*" end="\*/"

" -------------------------
" Destaques (linkagem)
" -------------------------
hi def link nexusKeyword Keyword
hi def link nexusBoolean Boolean
hi def link nexusNull Constant
hi def link nexusNumber Number
hi def link nexusFloat Number
hi def link nexusString String
hi def link nexusComment Comment
hi def link nexusOperator Operator
hi def link nexusConv Statement
hi def link nexusPunct Delimiter
hi def link nexusGroup Delimiter

let b:current_syntax = "nexus"
