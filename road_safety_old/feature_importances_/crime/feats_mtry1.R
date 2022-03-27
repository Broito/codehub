library(randomForest)
setwd("H:\\Crime\\Data Analysis\\2015 Crimes\\Regr_kd\\Samples1")
c("RSDQ_kd","FRSDQ_kd","LQ_kd","SQ_kd","WROD_kd","BL_kd")
type <- "RSDQ_kd"
ntree <- 500
select <- 1:43
# select <- c(40,42,35,34,37,32,38,33,41,22,39,24,31,36)
# select <- c(40,42,35,34,24,32,25,33,41,22,10,37,30,39,5,1)
# select <- c(40,42,35,32,33,34,10,39,22,25,41,30,38,31,36,43)
# select <- c(42,40,35,41,32,37,38,34,39,22,31,33,10,36,15,43)
# select <- c(35,42,40,34,32,37,33,38,22,39,36,31,1,43,9,30)
select <- c(42,40,35,34,32,38,33,37,22,39,31,36,30,5,1,43)

filename <- paste0(type, "_train", 9, ".csv")
train_data <- read.table(filename, header = T, sep = ",")
feats <- subset(train_data, select = select)
y <- train_data$RSDQ_kd  ### Attention change ... ###

## param mtry filtering
for (i in 1:length(feats)) {
  crime_rf <- randomForest(feats, y, mtry = i, ntree=ntree, importance = TRUE, corr.bias = TRUE, proximity = TRUE)
  err <- mean(crime_rf$mse)
  print(err)
}
