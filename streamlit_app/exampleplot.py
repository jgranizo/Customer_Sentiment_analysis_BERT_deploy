import pandas as pd
import plotly.express as px

# Example data for the chart
data = {
    "Brand": ["Apple", "Apple", "Apple", "Microsoft", "Microsoft", "Microsoft", "Google", "Google", "Google"] * 3,
    "Model": ["Model A"] * 9 + ["Model B"] * 9 + ["Model C"] * 9,
    "Sentiment": ["Negative", "Neutral", "Positive"] * 9,
    "Count": [50, 100, 150, 30, 60, 90, 20, 40, 70,
              40, 80, 120, 25, 55, 85, 15, 35, 65,
              60, 110, 160, 35, 65, 95, 25, 45, 75]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Filter data for an example brand (e.g., "Apple")
selected_brand = "Apple"
filtered_data = df[df["Brand"] == selected_brand]

# Plot a stacked bar chart using Plotly
fig = px.bar(
    filtered_data,
    x="Model",
    y="Count",
    color="Sentiment",
    title=f"Sentiment Classification for {selected_brand}",
    barmode="stack",
    labels={"Count": "Number of Comments", "Model": "Machine Learning Model"},
    color_discrete_map={"Negative": "red", "Neutral": "gray", "Positive": "green"}
)

# Display the figure
fig.show()
