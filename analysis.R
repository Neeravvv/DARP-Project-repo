setwd('C:/Users/NEERAV/OneDrive/Desktop/DARP/Project/Datasets')

t2018 = read.csv('top2018.csv')
t2019 = read.csv('top2019.csv')
t2020 = read.csv('top2020.csv')
t2021 = read.csv('top2021.csv')
t2022 = read.csv('top2022.csv')
t2023 = read.csv('top2023.csv')
t2024 = read.csv('top2024.csv')
t2025 = read.csv('top2025.csv')

# Add year column
t2018$year <- 2018
t2019$year <- 2019
t2020$year <- 2020
t2021$year <- 2021
t2022$year <- 2022
t2023$year <- 2023
t2024$year <- 2024
t2025$year <- 2025

# Q) What makes a song happy?

"""
Here, our target variable is happy probability.
we will compute correlation with all other variables except the identifying 
variables for all top songs across 2018-2025 to determine how they impact 
a song's impression as happy.
"""

combined.data <- bind_rows(t2018, t2019, t2020, t2021, t2022, t2023, t2024, t2025)



# tempo vs happy probability ######################################################

lm1 = lm(happy_probability ~ tempo_from_public_dataset, data = combined.data)
plot(combined.data$tempo_from_public_dataset, 
     combined.data$happy_probability, 
     mai = "tempo vs happiness",
     xlab = "tempo", 
     ylab = "happiness",
     pch = 16,
     col = 'lightblue')
abline(lm1, lwd = 2)
cor1 = cor(combined.data$tempo_from_public_dataset, combined.data$happy_probability)

"""
As we can see, there is a positive but low correlation(0.2296152) between tempo and the 
impression of a song as happy so, as the tempo of a song increases, we can assume 
that the probability that a person finds the song as happy also slightly increases.
"""

# danceability vs happy probability ###############################################

lm2 = lm(happy_probability ~ danceability_from_public_dataset, data = combined.data)
plot(combined.data$danceability_from_public_dataset, 
     combined.data$happy_probability,
     main = "danceability vs happiness",
     xlab = "danceability", 
     ylab = "happiness",
     pch = 16,
     col = 'turquoise')
abline(lm2, lwd = 2)
cor2 = cor(combined.data$danceability_from_public_dataset, combined.data$happy_probability)

"""
As we can see, the correlation between the danceability and happiness is positive
but close to 0 so, there is very low correlation between the two. As the danceability
of a song increases, the impression that a song is happy marginally increases.
"""

# acousticness vs happy probability ######################################################

lm3 = lm(happy_probability ~ acousticness, data = combined.data)
plot(combined.data$acousticness, 
     combined.data$happy_probability,
     main = "acousticness vs happiness",
     xlab = "acousticness", 
     ylab = "happiness",
     pch = 16,
     col = 'cyan')
abline(lm3, lwd = 2)
cor3 = cor(combined.data$acousticness, combined.data$happy_probability)

"""
As we can see, the correlation between the acousticness and happiness is nearly 0 
so, acousticness as no real effectiveness on happiness.
"""

# speechiness vs happy probability ######################################################

lm4 = lm(happy_probability ~ speechiness, data = combined.data)
plot(combined.data$speechiness, 
     combined.data$happy_probability,
     main = "speechiness vs happiness",
     xlab = "speechiness", 
     ylab = "happiness",
     pch = 16,
     col = 'skyblue')
abline(lm4, lwd = 2)
cor4 = cor(combined.data$speechiness, combined.data$happy_probability)

"""
As we can see, There is a low, negative correlation between the speechiness of a song
and happiness so, more spoken songs/ rap songs generally tend to be less joyful.
"""

# duration vs happy probability ######################################################

lm5 = lm(happy_probability ~ duration_minutes, data = combined.data)
plot(combined.data$duration_minutes, 
     combined.data$happy_probability,
     main = "duration vs happiness",
     xlab = "duration", 
     ylab = "happiness",
     pch = 16,
     col = 'powderblue')
abline(lm5, lwd = 2)
cor5 = cor(combined.data$duration_minutes, combined.data$happy_probability)

"""
As we can see, The correlation between duration and happiness is low but positive.
So, longer songs tend to be more happy but there doesn't seem to be more relationship
between the two.
"""

# loudness vs happy probability ######################################################

lm6 = lm(happy_probability ~ average_loudness, data = combined.data)
plot(combined.data$average_loudness, 
     combined.data$happy_probability,
     main = "loudness vs happiness",
     xlab = "loudness", 
     ylab = "happiness",
     pch = 16,
     col = 'lightpink')
abline(lm6, lwd = 2)
cor6 = cor(combined.data$average_loudness, combined.data$happy_probability)

"""
As we can see, there is a positive but low correlation between loudness and happiness
so, louder songs may tend to be happier.
"""

# dynamic complexity vs happy probability ######################################################

lm7 = lm(happy_probability ~ dynamic_complexity, data = combined.data)
plot(combined.data$dynamic_complexity, 
     combined.data$happy_probability,
     main = "complexity vs happiness",
     xlab = "dynamic complexity", 
     ylab = "happiness",
     pch = 16,
     col = "lightgreen")
abline(lm7, lwd = 2)
cor7 = cor(combined.data$dynamic_complexity, combined.data$happy_probability)

"""
As we can see, there is a strong, positive correlation between dynamic complexity
and happiness so, we can say that as a song becomes more dynamic and engaging, it 
makes people feel happy.
"""

# relaxed probability vs happy probability ######################################################

lm8 = lm(happy_probability ~ relaxed_probability, data = combined.data)
plot(combined.data$relaxed_probability, 
     combined.data$happy_probability,
     main = "relaxed vs happiness",
     xlab = "relaxed", 
     ylab = "happiness",
     pch = 16,
     col = "yellow3")
abline(lm8, lwd = 2)
cor8 = cor(combined.data$relaxed_probability, combined.data$happy_probability)

"""
As we can see, there is a positive but small correlation between the probability that
a song is relaxed and a song is happy so, songs that are calm may tend to be more 
joyful but it is not always necessary.
"""




########################################################################

# Q) Acousticness Over Time

# Average acousticness per year
acoustic_trend <- combined.data %>%
  group_by(year) %>%
  summarise(avg_acousticness = mean(acousticness, na.rm = TRUE))

# Plot
ggplot(acoustic_trend, aes(x = year, y = avg_acousticness)) +
  geom_line() +
  geom_point() +
  ggtitle("Average Acousticness Over Time")

"""
As we can see, average acousticness for the top songs was linearly 
increasing from 2018 to 2020. This shows that electronic music was still 
not popular before the lockdown. However, the increase in average 
acousticness started to decrease from 2020 t0 2022. 2022 to 2024 still
had more instrumental songs than electronic songs but 2024 onwards, there
was a rise in popularity of electronic music.
"""

##########################################################################

# Q) Which songs rank better, shorter or longer?

# Scatter plot
ggplot(combined.data, aes(x = duration_minutes, y = billboard_rank)) +
  geom_point() + 
  ggtitle("Duration vs Rank")

# Create top 20 indicator
combined.data$top20 <- ifelse(combined.data$billboard_rank <= 20, 1, 0)

# Average duration comparison
combined.data %>%
  group_by(top20) %>%
  summarise(avg_duration = mean(duration_minutes, na.rm = TRUE))


"""
So, the top 20 songs for the years 2018-2025 have a slightly lower duration
than the songs outside the top 20. This shows that highly popular songs 
have a fixed average during of 3 and half mins, showing that listeners
have a preferred range.
"""



##########################################################################

# Q) Is Music Becoming Formulaic?

# Variance by year
var_trend <- combined.data %>%
  group_by(year) %>%
  summarise(
    var_dance = var(danceability_from_public_dataset, na.rm = TRUE),
    var_tempo = var(tempo_from_public_dataset, na.rm = TRUE),
    var_acoustic = var(acousticness, na.rm = TRUE),
    var_duration = var(duration_minutes, na.rm = TRUE),
    var_complexity = var(dynamic_complexity, na.rm = TRUE),
    var_loudness = var(average_loudness, na.rm = TRUE),
    var_speechiness = var(speechiness, na.rm = TRUE)
  )

# Plot (stacked manually using base or ggplot)

ggplot(var_trend, aes(x = year, y = var_dance)) +
  geom_line() +
  ggtitle("Variance of Danceability Over Time")

ggplot(var_trend, aes(x = year, y = var_tempo)) +
  geom_line() +
  ggtitle("Variance of Tempo Over Time")

ggplot(var_trend, aes(x = year, y = var_acoustic)) +
  geom_line() +
  ggtitle("Variance of Acousticness Over Time")

ggplot(var_trend, aes(x = year, y = var_duration)) +
  geom_line() +
  ggtitle("Variance of Song Duration Over Time")

ggplot(var_trend, aes(x = year, y = var_complexity)) +
  geom_line() +
  ggtitle("Variance of Dynamic Complexity Over Time")

ggplot(var_trend, aes(x = year, y = var_loudness)) +
  geom_line() +
  ggtitle("Variance of Loudness Over Time")

ggplot(var_trend, aes(x = year, y = var_speechiness)) +
  geom_line() +
  ggtitle("Variance of speechiness Over Time")

"""

"""