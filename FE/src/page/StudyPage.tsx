import React, { useCallback, useEffect, useRef, useState } from 'react'
import SideBar from '../components/SideBar'
import { FaCircle } from "react-icons/fa";
import { LuCameraOff } from "react-icons/lu";
import { LuPause } from "react-icons/lu";
import { MdOutlineStop } from "react-icons/md";
import { VscDebugStart } from "react-icons/vsc";
import { IoReload } from "react-icons/io5";
import WebCam from '../components/WebCam';
import { instance } from '../api/axios';
interface Props {
  userid: string
}
const StudyPage = ({ userid }: Props) => {
  const [started_session, set_session] = useState<boolean>(false)
  const [pause, setPause] = useState<boolean>(false)
  const [time, setTime] = useState<number>(0);
  const [isCalibrated, setCalibrated] = useState<boolean>(false)
  const [request, setRequest] = useState<boolean>(false)
  const [focus_score, setFocusScore] = useState<number>(0)
  const [distraction_cnt, setdistraction_cnt] = useState<number>(0)
  const [isFocused, setFocused] = useState<boolean | null>(null)
  interface avgfocus_scoreType {
    count: number,
    avg: number,
    sum: number
  }
  const [avgfocus_score, setAvgfocus_score] = useState<avgfocus_scoreType>({
    count: 0,
    sum: 0,
    avg: 0,
  })
  interface DeepFocusType {
    bestTime: number,
    currentTime: number
  }
  const [DeepFocusTime, setDeepFocusTime] = useState<DeepFocusType>({
    bestTime: 0,
    currentTime: 0
  })
  // Calibration function
  const handle_calibrating = () => {
    setRequest(true);
  }
  const handdle_session_onclick = () => {
    set_session(!started_session)
    setTime(0);
    setPause(false)
    setCalibrated(false)
    setRequest(false)
    setFocused(null)
    setFocusScore(0)
    setDeepFocusTime({ bestTime: 0, currentTime: 0 })
    setAvgfocus_score({ count: 0, avg: 0, sum: 0 })
    setdistraction_cnt(0)
  }
  const handle_pause_onclick = () => {
    setPause(!pause)
  }
  const send_focus_score = async (avg_focus_score: number) => {
    const response = await instance.post("/create_timestamp", {
      avg_focus_score: avg_focus_score,
      userid: userid
    }, {
      headers: { 'Content-Type': 'application/json' }
    })
    const data = response.data
    if (data.status == 1) {
      console.log("timestamp created")
    }
  }
  const FocusTimerRef = useRef<any>(null)
  useEffect(() => {
    // If focused enough → start timer
    if (isFocused && !pause) {
      if (!FocusTimerRef.current) {
///        console.log('activated')
        FocusTimerRef.current = setInterval(() => {
          setDeepFocusTime(prev => {
            const current = prev.currentTime + 1
            // console.log(current, isFocused)
            const best = Math.max(prev.bestTime, current)
            return { currentTime: current, bestTime: best }
          })
        }, 1000)
      }
    }
    else if (isFocused && pause) {
      if (FocusTimerRef.current) {
        clearInterval(FocusTimerRef.current)
        FocusTimerRef.current = null
      }
    }
    // If not focused → stop timer
    else {
      if (FocusTimerRef.current) {
        clearInterval(FocusTimerRef.current)
        FocusTimerRef.current = null
      }

      setDeepFocusTime(prev => ({
        currentTime: 0,
        bestTime: prev.bestTime
      }))
    }

    // Cleanup when component unmounts
    return () => {
      if (FocusTimerRef.current) {
        clearInterval(FocusTimerRef.current)
        FocusTimerRef.current = null
      }
    }
  }, [isFocused, pause])
  useEffect(() => {
    if (focus_score >= 5) {

      ////console.log(avgfocus_score.count + 1)
      setAvgfocus_score({ avg: avgfocus_score.avg, count: avgfocus_score.count + 1, sum: avgfocus_score.sum + focus_score })




      if (focus_score <= 30 && focus_score != 0) {
        // setFocusScore(50)
        // setPause(true)
        // setdistraction_cnt(prev => prev + 1)
        // setFocused(false)
      } else if (focus_score <= 60) {
        setFocused(false)
      } else if (focus_score <= 70) {
        setFocused(true)
      } else if (focus_score <= 100) {
        setFocused(true)
      }
    }
  }, [focus_score])
  useEffect(() => {
    let interval: any = null;
    if (!pause && isFocused != null) {
      interval = setInterval(() => {
        setTime(prev =>{
          
          return prev+1;
        })

      }, 1000)
    } else {
      clearInterval(interval)
    }

    return () => clearInterval(interval)


  }, [pause, started_session,isFocused])
  useEffect(()=>{
    if((time+1) % 60 == 0 && (time+1) != 0){
            let new_avg = Math.floor(avgfocus_score.sum / (avgfocus_score.count + 1))
            setAvgfocus_score({ avg: new_avg, count: 0, sum: 0 })
            send_focus_score(new_avg)
          }
  },[time])
  
  let hour = Math.floor(time / 3600) % 24
  let formated_hour = (hour >= 10) ? `${hour}` : `0${hour}`
  let minute = Math.floor(time / 60) % 60
  let formated_minute = (minute >= 10) ? `${minute}` : `0${minute}`
  let second = time % 60
  let formated_second = (second >= 10) ? `${second}` : `0${second}`
  let deepfocustime_msg = ''
  if (DeepFocusTime.bestTime / 3600 >= 1) {
    deepfocustime_msg = `${Math.floor(DeepFocusTime.bestTime / 3600)} hour(s)`
  } else if (DeepFocusTime.bestTime / 60 >= 1) {
    deepfocustime_msg = `${Math.floor(DeepFocusTime.bestTime / 60)} minute(s)`
  } else {
    deepfocustime_msg = `${DeepFocusTime.bestTime} second(s)`
  }
  let focus_comment = ''
  if (focus_score >= 5) {
    if (focus_score <= 30) {
      // alert("Focus on your study!!!")
      // focus_comment = 'Terrible'
    } else if (focus_score <= 60) {
      focus_comment = 'Decent'
    } else if (focus_score <= 70) {
      focus_comment = 'Great'
    } else {
      focus_comment = 'Excellent'
    }
  } else {
    focus_comment = 'Waiting for stream'
  }
  return (
    <>


      <SideBar />
      <div className="study-page">

        <div className="study-box">
          <div className="study-page-title">
            <h1>Live Study Session</h1>
            {
              started_session ?
                <p id='live'><FaCircle /> Live</p>
                :
                <p id='waiting'><FaCircle /> Waitng</p>
            }

          </div>

          <div className="camera-box">
            {
              !started_session ?
                <>
                  <LuCameraOff className='not' />
                  <h2>Camera Not Detected</h2>
                  <p>Please ensure your camera is connected and you've granted the neccessary permissions in your browser</p>
                  <button><IoReload /> Retry Connection</button>
                </>
                :

                <>
                  <WebCam isCalibrated={isCalibrated} request={request} setFocusScore={setFocusScore} setCalibrated={setCalibrated} pause={pause} started_session={started_session} />
                </>
            }

          </div>
          <div className="study-time">
            <div className="time-box">
              <div className="time-card">
                {
                  started_session ?
                    <h2 className='live' id='hour'>{formated_hour}</h2>
                    :
                    <h2>00</h2>
                }
                <p>HOURS</p>
              </div>
              <div className="time-card">
                {
                  started_session ?
                    <h2 className='live' id='minute'>{formated_minute}</h2>
                    :
                    <h2>00</h2>
                }
                <p>MINUTES</p>
              </div>
              <div className="time-card">
                {
                  started_session ?
                    <h2 className='live' id='second'>{formated_second}</h2>
                    :
                    <h2>00</h2>
                }
                <p>SECONDS</p>
              </div>
            </div>
            <div className="session-option">

              {
                started_session ?
                  <>
                    <button id='pause' onClick={handle_pause_onclick}><LuPause /> Pause</button>
                    <button onClick={handdle_session_onclick} id='stop'><MdOutlineStop /> Stop Session</button>
                    <button id='stop' onClick={handle_calibrating}><MdOutlineStop /> Calibrate</button>
                  </>

                  :
                  <button onClick={handdle_session_onclick} id='start'><VscDebugStart /> Start Session</button>
              }


            </div>
          </div>

        </div>
        <div className="study-analysis">
          <h2>Real-Time Analysis</h2>
          <div className="focus-score">
            <p>Current Focus Score</p>
            {started_session ?
              <>
                <h1 className='score'>{focus_score}</h1>
                <p className='score'>{focus_comment}</p>
              </>
              :
              <>
                <h1>--</h1>
                <p>Waiting for stream...</p>
              </>
            }

          </div>
          <h2>Session Insights</h2>
          <div className="session-insight">
            <div className="insight-card">
              <p>AVG. FOCUS</p>
              {
                started_session ?
                  <h3 className='live'>{avgfocus_score.avg}</h3>
                  :
                  <h3>--</h3>
              }
            </div>
            <div className="insight-card">
              <p>DEEP FOCUS</p>
              {
                started_session ?
                  <h3 className='live'>{deepfocustime_msg}</h3>
                  :
                  <h3>--</h3>
              }
            </div>
            <div className="insight-card" id='distraction-alert'>
              <p>DISTRACTION ALERTS</p>
              {
                started_session ?
                  <h3 className='live'>{distraction_cnt}</h3>
                  :
                  <h3>--</h3>
              }
            </div>
          </div>
        </div>

      </div>
    </>

  )
}

export default StudyPage