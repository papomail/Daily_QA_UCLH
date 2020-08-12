import plotly.express as px



fig2 = px.bar(dict(a=[1,2], b=[4,5]), barmode="group", error_y=[0.5,0.5])
fig2.for_each_trace(lambda t: t.update(error_y_color=t.marker.color))
fig2.show()