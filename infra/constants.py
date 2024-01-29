DATABASE_NAME = "infra/sqlite/main.db"
SQL_FILE = "./infra/sqlite/start_up.sql"
SQL_FILE_TEST = "../infra/sqlite/start_up.sql"

STARTING_BITCOIN_AMOUNT = 1
WALLETS_LIMIT = 3
TOKEN_HEX_BYTES_NUM = 32

NotEnoughBitcoinErrorCode = 404
TransactionBetweenSameWalletErrorCode = 404
WalletPermissionErrorCode = 404
WalletsLimitErrorCode = 404
InvalidApiKeyErrorCode = 401
DoesNotExistErrorCode = 404
