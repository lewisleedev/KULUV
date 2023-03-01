import datetime, kult
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Or you'll get an error
import matplotlib.pyplot as plt
import calmap
from flask import Flask, render_template, request

app = Flask(__name__)

# Define the index page route
@app.route('/')
def index():
    return render_template('index.html')

# Define route for heatmap page
@app.route('/heatmap', methods=['POST'])
def heatmap():
    # Get student ID from form
    student_id = request.form['student_id']
    
    # Call kult.Client() class to get library usage data
    client = kult.Client(student_id)
    data = client.get_seat_history(20)
    
    # Create Pandas dataframe and transform it for heatmap
    df = pd.DataFrame(data)
    df['start_time'] = pd.to_datetime(pd.to_datetime(df['start_time']).dt.date)
    df['duration'] = df['duration'].apply(lambda x: round(x.total_seconds() / 3600, 1))
    df = df.groupby(df['start_time']).sum(numeric_only=True)

    print(df)
    
    # Create calendar heatmap with calmap
    plt.figure(figsize=(10, 7))
    # plt.title(f"Library Usage for Student {student_id}")

    calmap.calendarplot(df['duration'], cmap='Reds', linewidth = 2, vmin = 0.3, vmax = 10,
                        daylabels='MTWTFSS',dayticks=[0, 2, 4, 6])
    
    # Convert Matplotlib plot to HTML format
    plot_html = mpl_to_html(plt.gcf())
    
    # Render heatmap in HTML template
    return render_template('heatmap.html', plot=plot_html)

# Function to convert Matplotlib plot to HTML format
def mpl_to_html(fig):
    """Converts a Matplotlib figure to an HTML image tag."""
    from io import BytesIO
    import base64
    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close(fig)
    return f'<img src="data:image/png;base64,{image_base64}"/>'

if __name__ == '__main__':
    app.run()
