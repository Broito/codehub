library(corrplot)
library(Hmisc)
setwd("H:\\Crime\\Data Analysis\\2015 Crimes\\R")
filename<-"Crimes_cls_feats - kd.csv"
fi <- read.csv(filename)
cor_matrix <- cor(fi[2:45])
df_cor_matrix <- as.data.frame(cor_matrix)
corrplot(cor_matrix, type = "lower", method = "number")

# rcorr(as.matrix(fi[2:45]))