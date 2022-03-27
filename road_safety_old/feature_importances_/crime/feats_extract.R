library(randomForest)
setwd("H:\\Crime\\Data Analysis\\2015 Crimes\\Regr_kd\\Samples1")
c("RSDQ_kd","FRSDQ_kd","LQ_kd","SQ_kd","WROD_kd","BL_kd")
type <- "RSDQ_kd"
ntree <- 1000
select <- 1:43
# select <- c(10,22,24,25,32,33,34,35,36,37,38,39,40,41,42)
select <- c(5,10,22,24,25,30,32,33,34,35,37,39,40,41,42)
# select <- c(10,22,25,30,31,32,33,34,35,36,38,39,40,41,42,43)
# select <- c(10,15,22,31,32,33,34,35,36,37,38,39,40,41,42,43)
# select <- c(9,22,30,31,32,33,34,35,36,37,38,39,40,42,43
# select <- c(1,5,22,30,31,32,33,34,35,36,37,38,39,40,42)

Timp <- 0
Mse <- 0
Rsq <- 0
for (i in c(1:15)) {
  print(i)
  filename <- paste0(type, "_train", i, ".csv")
  train_data <- read.table(filename, header = T, sep = ",")
  feats <- subset(train_data, select = select)
  y <- train_data$RSDQ_kd  ### Attention change ... ###
  
  crime_rf <- randomForest(feats,y, importance = TRUE, corr.bias = TRUE, proximity = TRUE, ntree = ntree)
  print(paste("Mean RMSE: ", sqrt(mean(crime_rf$mse)), "; Mean RSQ: ", mean(crime_rf$rsq)))
  imp <- importance(crime_rf)
  Timp <- Timp + imp
  Mse <- Mse + crime_rf$mse
  Rsq <- Rsq + crime_rf$rsq
}
paste("write ", type)
print(mean(Mse)/15)
print(mean(Rsq)/15)
# print(crime_rf$mtry)
# plot(crime_rf)
# write.csv(Timp/15, file = paste0("..\\Class1\\3 imp_sort ", type, ".csv"), quote = T)

