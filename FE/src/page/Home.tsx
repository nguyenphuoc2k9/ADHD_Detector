import SideBar from '../components/SideBar'
import { LineChart } from '@mui/x-charts/LineChart'
import { IoSend } from "react-icons/io5";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
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
import { useEffect, useState } from 'react';
import { instance } from '../api/axios';
import gif from '../assets/Rolling@1x-1.0s-200px-200px.gif'
interface Props {
  userid: string
}
const Home = ({ userid }: Props) => {
  const [PlotData, setPlotData] = useState<any[]>()
  const [sortType, setSortType] = useState<string>('today')
  const [label, setLabel] = useState<string[]>(['1AM', '2AM', '3AM', '4AM', '5AM', '6AM', '7AM', '8AM', '9AM', '10AM', '11AM', '12AM', '1PM', '2PM', '3PM', '4PM', '5PM', '6PM', '7PM', '8PM', '9PM', '10PM', '11PM', '12PM'])
  const [chatHistory, setChatHistory] = useState<string[]>([])
  const [isLoading, setLoading] = useState<boolean>(false)
  const handle_submit_chat = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const form = new FormData(e.currentTarget)
    const user_chat = form.get("user_chat") as string;
    e.currentTarget.reset()
    setLoading(true)
    setChatHistory([...chatHistory, user_chat])
    const response = await instance.post("/call_ai", { user_chat: user_chat, userid: userid },{headers: {"Content-Type":'application/json'}})
    setLoading(false)
    setChatHistory([...chatHistory, user_chat,response.data.ai_chat])
  }
  const handle_change_type = (type: string) => {
    if (type == 'today') {
      setLabel(['1AM', '2AM', '3AM', '4AM', '5AM', '6AM', '7AM', '8AM', '9AM', '10AM', '11AM', '12AM', '1PM', '2PM', '3PM', '4PM', '5PM', '6PM', '7PM', '8PM', '9PM', '10PM', '11PM', '12PM'])

    } else if (type == 'month') {
      let now = new Date()
      let list = []
      let month_array = ['', 'Jan', 'Feb', 'Mar', 'Ap', 'May', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      let current_month = month_array[now.getMonth()]
      for (let i = 1; i <= now.getDate(); i++) {
        list.push(`${current_month} ${i}th`)
      }
      setLabel(list)

    } else if (type == 'week') {
      setLabel(["Mon", 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    } else if (type == 'year') {
      setLabel(['Jan', 'Feb', 'Mar', 'Ap', 'May', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    }
    setSortType(type)
  }
  const process_plot_data = (data: any[]) => {
    let list: any[] = []
    console.log(data)
    if (data) {
      if (sortType == 'today') {
        list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for (let i = 0; i < data.length; i++) {
          list[data[i]._id.hour - 1] = Math.floor(data[i].avg_focus)
        }
      } else if (sortType == 'month') {
        
        list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for (let i = 0; i < data.length; i++) {
          list[i] = Math.floor(data[i].avg_focus)
        }

      } else if (sortType == 'week') {
        list = [0, 0, 0, 0, 0, 0, 0]
        for (let i = 0; i < data.length; i++) {
          list[i] = Math.floor(data[i].avg_focus)
        }
      } else if (sortType == 'year') {
        list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for (let i = 0; i < data.length; i++) {
          list[i] = Math.floor(data[i].avg_focus)
        }
      }
    }
    // console.log(sortType, list)
    return list

  }
  const get_plot_data = async () => {
    let end_point = ''
    // console.log(sortType)
    if (sortType == 'today') {
      end_point = '/get_timestamp_today'
    } else if (sortType == 'week') {
      end_point = '/get_timestamp_week'
    }
    else if (sortType == 'month') {
      end_point = '/get_timestamp_month'
    }
    else if (sortType == 'year') {
      end_point = '/get_timestamp_year'
    }
    const response = await instance.post(end_point, { userid: userid }, { headers: { "Content-Type": 'application/json' } })
    const data: any[] = response.data
    console.log(data)
    setPlotData(process_plot_data(data))
  }


  const data = {
    labels: label,
    datasets: [
      {
        label: 'Focus Score ',
        data: PlotData,
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
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
      }

    },
    scales: {
      x: {
        ticks: {
          color: '#d8dde6ff'
        },
        grid: {
          color: "rgba(55,65,81,0.5)",
          borderColor: 'transparent'
        }
      },
      y: {
        ticks: {
          color: '#d8dde6ff'
        },
        grid: {
          color: "rgba(55,65,81,0.2)",
          borderColor: 'transparent'
        }
      },
    }

  }
  useEffect(() => {
    get_plot_data()
  }, [sortType])
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
          {/* <div className="statistic">
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
          </div> */}
          <div className="graph">
            <div className="graph-title">
              {sortType == 'today'
                ?
                <h3>Focus Score {sortType}</h3>
                :
                <h3>Focus Score this {sortType}</h3>
              }

            </div>
            <div className="progress-scale">
              <button onClick={() => handle_change_type("today")} className={sortType == 'today' ? 'active' : ''}>Today</button>
              <button onClick={() => handle_change_type("week")} className={sortType == 'week' ? 'active' : ''}>This Week</button>
              <button onClick={() => handle_change_type("month")} className={sortType == 'month' ? 'active' : ''}>This Month</button>
              <button onClick={() => handle_change_type("year")} className={sortType == 'year' ? 'active' : ''}>This Year</button>
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
            {chatHistory.map((text, i) => {
              if (i % 2 == 0) {
                return (
                  <div className="user-chat">
                    <p>{text}</p>
                  </div>
                )
              } else {
                return (
                  <div className="chatbot-chat">
                <ReactMarkdown 
                // remarkGfm handles bolding and list recognition perfectly
                  remarkPlugins={[remarkGfm]} 
        // You can use a custom component for the bold text or list items 
        // if you wanted specific styling not handled by CSS
        components={{
            // This component ensures the list items are rendered properly
            ul: ({ node, ...props }) => <ul style={{ listStyleType: 'disc', paddingLeft: '20px' }} {...props} />,
            // This component ensures bold text has an accent color
            strong: ({ node, ...props }) => <strong style={{ color: '#007bff' }} {...props} />,
        }}
      >
        {text}
      </ReactMarkdown>
                  </div>
                )
              }

            })}


            {

            }




          </div>
          <div className="chatbot-input">
            <form action="" method="post" onSubmit={(e) => handle_submit_chat(e)}>
              <input type="text" name='user_chat' placeholder='Ask AI' />
              <button type='submit'>{isLoading ? <img src={gif}/> : <IoSend />}</button>
            </form>
          </div>
        </div>
      </div>

    </>

  )
}

export default Home