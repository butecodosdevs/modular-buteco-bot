import random
import plotly.graph_objects as go

class PoliticalGraph:
    def _adjust_position(self, x, y, placed_labels):
        """Adjust the position of the label to avoid overlap."""
        min_dist = 0.5
        while any(
            abs(y - py) < min_dist and abs(x - px) < min_dist for px, py in placed_labels
        ):
            y -= 0.2
        placed_labels.append((x, y))
        return x, y


    def _add_point(self, fig, x, y, color):
        """Add a point to the figure."""
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers",
                marker=dict(color=color, size=10),
                showlegend=False,
            )
        )


    def _add_label(self, fig, x, y, label, color):
        """Add a label to the figure."""
        xAlign = "center"
        yAlign = "top"

        if y < 0:
            yAlign = "bottom"

        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                text=[f"{label}"],
                mode="text",
                textposition=f"{yAlign} {xAlign}",
                textfont=dict(color=color, size=17),
                showlegend=False,
            )
        )


    def _add_quadrants(self, fig):
        """Add quadrants to the figure."""
        fig.add_shape(
            type="rect",
            x0=0,
            x1=-10,
            y0=0,
            y1=10,
            fillcolor="red",
            opacity=0.1,
            line=dict(width=0),
        )
        fig.add_shape(
            type="rect",
            x0=0,
            x1=10,
            y0=0,
            y1=10,
            fillcolor="blue",
            opacity=0.1,
            line=dict(width=0),
        )
        fig.add_shape(
            type="rect",
            x0=0,
            x1=-10,
            y0=0,
            y1=-10,
            fillcolor="lightgreen",
            opacity=0.1,
            line=dict(width=0),
        )
        fig.add_shape(
            type="rect",
            x0=0,
            x1=10,
            y0=0,
            y1=-10,
            fillcolor="purple",
            opacity=0.1,
            line=dict(width=0),
        )


    def _add_axes(self, fig):
        """Add axes to the figure."""
        fig.add_trace(
            go.Scatter(
                x=[-10, 10],
                y=[0, 0],
                mode="lines",
                line=dict(color="black", width=2),
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[0, 0],
                y=[-10, 10],
                mode="lines",
                line=dict(color="black", width=2),
                showlegend=False,
            )
        )


    def _add_axis_labels(self, fig):
        """Add axis labels to the figure."""
        fig.add_trace(
            go.Scatter(
                x=[10],
                y=[0],
                text=["RIGHT"],
                textposition="middle right",
                mode="text",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[-10],
                y=[0],
                text=["LEFT"],
                textposition="middle left",
                mode="text",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[0],
                y=[10],
                text=["AUTHORITARIAN"],
                textposition="top center",
                mode="text",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[0],
                y=[-10],
                text=["LIBERTARIAN"],
                textposition="bottom center",
                mode="text",
                showlegend=False,
            )
        )


    def create_figure(self, points):
        """Create the political compass figure."""
        colors = [
            "red",
            "blue",
            "green",
            "purple",
            "orange",
            "magenta",
            "teal",
            "navy",
        ]
        random.shuffle(colors)

        fig = go.Figure()
        placed_labels = []

        for x, y, label in points:
            x_adj, y_adj = self._adjust_position(x, y, placed_labels)
            color = random.choice(colors)
            self._add_point(fig, x, y, color)
            self._add_label(fig, x, y_adj, label, color)

        self._add_quadrants(fig)
        self._add_axes(fig)
        self._add_axis_labels(fig)

        fig.update_layout(
            xaxis=dict(range=[-11, 11], tickmode="linear", tick0=-10, dtick=2.0),
            yaxis=dict(range=[-11, 11], tickmode="linear", tick0=-10, dtick=2.0),
            plot_bgcolor="white",
            title="Buteco Political Compass",
            title_x=0.5,
            template="plotly_white",
        )

        return fig
