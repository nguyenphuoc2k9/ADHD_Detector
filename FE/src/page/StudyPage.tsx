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
  userid?: string
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

  // Audio and Throttling Refs
  const alertAudio = useRef<HTMLAudioElement | null>(null);
  const lastAlertTimeRef = useRef<number>(0);

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

  // Initialize Alert Sound
  useEffect(() => {
    alertAudio.current = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3');
    if (alertAudio.current) {
      alertAudio.current.volume = 0.6;
    }
  }, []);

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
    try {
      const response = await instance.post("/create_timestamp", {
        avgfocus_score: avg_focus_score,
        userid: userid
      }, {
        headers: { 'Content-Type': 'application/json' }
      })
      if (response.data.status == 1) {
        console.log("timestamp created")
      }
    } catch (err) {
      console.error("Failed to send focus score", err)
    }
  }

  const FocusTimerRef = useRef<any>(null)

  useEffect(() => {
    if (isFocused && !pause) {
      if (!FocusTimerRef.current) {
        FocusTimerRef.current = setInterval(() => {
          setDeepFocusTime(prev => {
            const current = prev.currentTime + 1
            const best = Math.max(prev.bestTime, current)
            return { currentTime: current, bestTime: best }
          })
        }, 1000)
      }
    }
    else {
      if (FocusTimerRef.current) {
        clearInterval(FocusTimerRef.current)
        FocusTimerRef.current = null
      }

      if (!isFocused) {
        setDeepFocusTime(prev => ({
          currentTime: 0,
          bestTime: prev.bestTime
        }))
      }
    }

    return () => {
      if (FocusTimerRef.current) {
        clearInterval(FocusTimerRef.current)
      }
    }
  }, [isFocused, pause])

  // Focus Score Logic & Audio Trigger
  useEffect(() => {
    if (focus_score >= 5) {
      setAvgfocus_score(prev => ({
        ...prev,
        count: prev.count + 1,
        sum: prev.sum + focus_score
      }))

      // Play sound if score < 30 (with 5-second throttle to avoid sound spam)
      const now = Date.now();
      if (focus_score < 50 && started_session && !pause) {
        if (now - lastAlertTimeRef.current > 5000) { 
          alertAudio.current?.play().catch(e => console.log("Audio play blocked", e));
          setdistraction_cnt(prev => prev + 1);
          lastAlertTimeRef.current = now;
        }
      }

      if (focus_score <= 60) {
        setFocused(false)
      } else {
        setFocused(true)
      }
    }
  }, [focus_score, started_session, pause])

  useEffect(() => {
    let interval: any = null;
    if (!pause && started_session && isFocused !== null) {
      interval = setInterval(() => {
        setTime(prev => prev + 1);
      }, 1000)
    } else {
      clearInterval(interval)
    }
    return () => clearInterval(interval)
  }, [pause, started_session, isFocused])

  useEffect(() => {
    if ((time + 1) % 60 == 0 && (time + 1) != 0) {
      let new_avg = Math.floor(avgfocus_score.sum / (avgfocus_score.count + 1))
      setAvgfocus_score({ avg: new_avg, count: 0, sum: 0 })
      send_focus_score(new_avg)
    }
  }, [time])

  // Formatting Logic
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
    if (focus_score <= 30) focus_comment = 'Low Focus!'
    else if (focus_score <= 60) focus_comment = 'Decent'
    else if (focus_score <= 70) focus_comment = 'Great'
    else focus_comment = 'Excellent'
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
            {started_session ? 
              <p id='live'><FaCircle /> Live</p> : 
              <p id='waiting'><FaCircle /> Waiting</p>
            }
          </div>

          <div className="camera-box">
            {!started_session ? (
              <>
                <LuCameraOff className='not' />
                <h2>Camera Not Detected</h2>
                <p>Ensure your camera is connected and permissions are granted.</p>
                <button><IoReload /> Retry Connection</button>
              </>
            ) : (
              <WebCam 
                isCalibrated={isCalibrated} 
                request={request} 
                setFocusScore={setFocusScore} 
                setCalibrated={setCalibrated} 
                pause={pause} 
                started_session={started_session} 
              />
            )}
          </div>

          <div className="study-time">
            <div className="time-box">
              <div className="time-card">
                <h2>{started_session ? formated_hour : "00"}</h2>
                <p>HOURS</p>
              </div>
              <div className="time-card">
                <h2>{started_session ? formated_minute : "00"}</h2>
                <p>MINUTES</p>
              </div>
              <div className="time-card">
                <h2>{started_session ? formated_second : "00"}</h2>
                <p>SECONDS</p>
              </div>
            </div>

            <div className="session-option">
              {started_session ? (
                <>
                  <button id='pause' onClick={handle_pause_onclick}><LuPause /> {pause ? 'Resume' : 'Pause'}</button>
                  <button onClick={handdle_session_onclick} id='stop'><MdOutlineStop /> Stop Session</button>
                  <button id='stop' onClick={handle_calibrating}><MdOutlineStop /> Calibrate</button>
                </>
              ) : (
                <button onClick={handdle_session_onclick} id='start'><VscDebugStart /> Start Session</button>
              )}
            </div>
          </div>
        </div>

        <div className="study-analysis">
          <h2>Real-Time Analysis</h2>
          <div className="focus-score">
            <p>Current Focus Score</p>
            {started_session ? (
              <>
                <h1 className='score'>{focus_score}</h1>
                <p className='score'>{focus_comment}</p>
              </>
            ) : (
              <>
                <h1>--</h1>
                <p>Waiting for stream...</p>
              </>
            )}
          </div>
          <h2>Session Insights</h2>
          <div className="session-insight">
            <div className="insight-card">
              <p>AVG. FOCUS</p>
              <h3>{started_session ? avgfocus_score.avg : "--"}</h3>
            </div>
            <div className="insight-card">
              <p>DEEP FOCUS</p>
              <h3>{started_session ? deepfocustime_msg : "--"}</h3>
            </div>
            <div className="insight-card" id='distraction-alert'>
              <p>DISTRACTION ALERTS</p>
              <h3>{started_session ? distraction_cnt : "--"}</h3>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default StudyPage