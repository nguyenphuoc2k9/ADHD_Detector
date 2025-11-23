import SideBar from '../components/SideBar'
import { LineChart } from '@mui/x-charts/LineChart'
import { IoSend } from "react-icons/io5";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Registering the components is crucial for ChartJS to work correctly.
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);
import { Line } from "react-chartjs-2"
import "./style.css"

const Home = () => {
  const data = {
    labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
    datasets: [
      {
        label: 'Focus Time (Minutes)',
        data: [100, 200, 300, 150, 450, 250, 350],
        borderColor: '#2563EB', // Blue-600 for line color
        backgroundColor: 'rgba(37, 99, 235, 0.15)', // Light blue fill
        tension: 0.4,
        pointBackgroundColor: '#2563EB',
        pointRadius: 6, // Larger points
        pointHoverRadius: 8,
      }
    ]
  }
  const option = {
    backgroundColor: 'rgba(0,0,0,0.5)',
    responsive: true,
    maintainAspectRatio:false,
    plugins: {
      legend: {
        display:false,
      },
      title: {
        display:false,
      }

    },
    scales:{
      x:{
        ticks:{
          color:'#d8dde6ff'
        },
        grid:{
          color:"rgba(55,65,81,0.5)",
          borderColor:'transparent'
        }
      },
      y:{
        ticks:{
          color:'#d8dde6ff'
        },
        grid:{
          color:"rgba(55,65,81,0.2)",
          borderColor:'transparent'
        }
      },
    }

  }
  const chartKey = JSON.stringify(data.datasets) + JSON.stringify(option);
  return (
    <>
      <SideBar />
      <div className="home">
        <div className="dashboard">
          <div className="front-text">
            <h1>Dashboard</h1>
            <p>Welcome back, here's a sumary of your study performance</p>
          </div>
          <div className="statistic">
            <div className="box">
              <h4>Total Focus Time Today</h4>
              <h1>4h 32m</h1>
              <p>+12%</p>
            </div>
            <div className="box">
              <h4>Total Focus Time Today</h4>
              <h1>4h 32m</h1>
              <p>+12%</p>
            </div>
            <div className="box">
              <h4>Total Focus Time Today</h4>
              <h1>4h 32m</h1>
              <p>+12%</p>
            </div>
          </div>
          <div className="graph">
            <div className="graph-title">
              <h3>Focus Time This Month</h3>
            </div>
            <div className="progress-scale">
              <button>Today</button>
              <button>This Week</button>
              <button>This Month</button>
              <button>This Year</button>
            </div>
            <div className="graph-box">
                <Line
              key={chartKey}
              data={data}
              options={option}
            />
            </div>
            {/* <LineChart
              xAxis={[
                {
                  data: [1, 2, 3, 5, 8, 10]

                }]}
              series={[
                {
                  data: [2, 5.5, 2, 8.5, 1.5, 5],
                },
              ]}
              height={600}
              sx={{
                // Set ALL axis lines (X and Y) to white
                "& .MuiChartsAxis-line": {
                  stroke: "white",
                },

                // Set ALL axis ticks (X and Y) to white
                "& .MuiChartsAxis-tick": {
                  stroke: "white",
                },

                // Set ALL tick labels (X and Y text) to white
                "& .MuiChartsAxis-tickLabel": {
                  fill: "white",
                },

                // Optional: Change the color of the grid lines if you have them enabled
                "& .MuiChartsGrid-line": {
                  stroke: "rgba(255, 255, 255, 0.3)", // Light grey for subtle grid
                },
                
              }}
            /> */}
            

          </div>
        </div>
        <div className="chatbot">
          <div className="chatbot-title">
            <h1>AI Study Coach</h1>
            <p>Your personal assistant</p>
          </div>
          <div className="chatbot-box">
            <div className="chatbot-box-introduction">
              <p>Hello! How can I help you optimize your study plan today?</p>

            </div>
            <div className="chatbot-box-suggestion">
              <p>Help me plan my week.</p>
            </div>
            <div className="user-chat">
              <p>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Optio aperiam natus cupiditate quos amet blanditiis officia consectetur ea eos adipisci, excepturi quia facere facilis cum itaque ad perferendis alias modi?</p>
            </div>
            <div className="chatbot-chat">
              <p>Lorem ipsum dolor, sit amet consectetur adipisicing elit. Eaque enim voluptate non rerum, temporibus ad odio nostrum maiores quidem dolorum rem, repudiandae repellat sunt atque. Blanditiis quia non neque fugit.</p>
            </div>
            <div className="user-chat">
              <p>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Optio aperiam natus cupiditate quos amet blanditiis officia consectetur ea eos adipisci, excepturi quia facere facilis cum itaque ad perferendis alias modi?</p>
            </div>
            <div className="user-chat">
              <p>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Optio aperiam natus cupiditate quos amet blanditiis officia consectetur ea eos adipisci, excepturi quia facere facilis cum itaque ad perferendis alias modi?</p>
            </div>
            <div className="chatbot-chat">
              <p>Lorem ipsum dolor, sit amet consectetur adipisicing elit. Eaque enim voluptate non rerum, temporibus ad odio nostrum maiores quidem dolorum rem, repudiandae repellat sunt atque. Blanditiis quia non neque fugit.</p>
            </div>
            <div className="user-chat">
              <p>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Optio aperiam natus cupiditate quos amet blanditiis officia consectetur ea eos adipisci, excepturi quia facere facilis cum itaque ad perferendis alias modi?</p>
            </div>




          </div>
          <div className="chatbot-input">
            <form action="" method="post">
              <input type="text" placeholder='Ask AI' />
              <button type='submit'><IoSend /></button>
            </form>

          </div>
        </div>
      </div>

    </>

  )
}

export default Home