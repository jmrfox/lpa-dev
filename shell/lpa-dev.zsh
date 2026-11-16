# Kept so existing ~/.zshrc lines keep working. The integration now lives in
# lpa-dev.sh (bash and zsh); new setups source that file instead.
source "${${(%):-%x}:A:h}/lpa-dev.sh"
