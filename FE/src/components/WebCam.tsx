import React, { useCallback, useEffect, useRef, useState } from 'react'
import Webcam from 'react-webcam'
import { instance } from '../api/axios'
interface Props {
    started_session: boolean,
    pause: boolean,
    
    request:boolean,
    isCalibrated: boolean,
    setCalibrated: React.Dispatch<React.SetStateAction<boolean>>,
    setFocusScore: React.Dispatch<React.SetStateAction<number>>
}

const WebCam = ({ setFocusScore,request,started_session, pause, isCalibrated, setCalibrated }: Props) => {
    const videoConstraints = {
        facingMode: 'user'
    }
    const webcamRef = useRef<Webcam>(null)
    const [frameData, setFrameData] = useState<string | null>(null)
    const [isProcessing, setIsProcessing] = useState(false)
    const intervalRef = useRef<any>(null)
    const CAPTURE_INTERVAL_MS = 100
    const isCalibratingRef = useRef(false) // prevent overlapping calibration
    
    // Calibration function
    const Calibrating = async (base64image: string) => {
        if (isCalibratingRef.current) return // avoid multiple calls
        isCalibratingRef.current = true

        try {
            const response = await instance.post("/calibrate", {
                
                image:JSON.stringify(base64image)
            },
            {
                headers: { 'Content-Type': 'application/json' }
            }
            
            )
            const data = await response.data
            if (data.state === 'done') {
                setCalibrated(true)
                console.log('Calibration done')
            }
        } catch (error) {
            console.log('Calibration error:', error)
        } finally {
            isCalibratingRef.current = false
        }
    }
    
    // Frame processing function
    const sendFrameToModule = async (base64image: string) => {
        try {
             const response = await instance.post("/process", {
                
                image:JSON.stringify(base64image)
            },
            {
                headers: { 'Content-Type': 'application/json' }
            }
            
            )
            const data = await response.data
            setFocusScore(Math.floor(data.focus_score*100))
        } catch (error) {
            console.log('Processing error:', error)
        }
    }

    // Capture frame callback
    const captureFrame = useCallback(async () => {
        if (!webcamRef.current) return

        const imageSrc = webcamRef.current.getScreenshot()
        if (!imageSrc) return

        setFrameData(imageSrc)
        
        if(isCalibrated)
        {
            sendFrameToModule(imageSrc)
        }
        else if (request && !isCalibrated){
            await Calibrating(imageSrc)
        }
    }, [isCalibrated,request])

    // Start and stop frame collection
    const startCollection = () => {
        if (intervalRef.current) return
        intervalRef.current = setInterval(captureFrame, CAPTURE_INTERVAL_MS)
        setIsProcessing(true)
        console.log('Frame collection started')
    }

    const stopCollection = () => {
        if (intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
            setIsProcessing(false)
            console.log('Frame collection stopped')
        }
    }

    // Handle session start/pause
    useEffect(() => {
        if (started_session && !pause) {
            startCollection()
        } else {
            stopCollection()
        }

        return () => stopCollection()
    }, [started_session, pause, captureFrame])

    return (
        <Webcam
            ref={webcamRef}
            audio={false}
            videoConstraints={videoConstraints}
            screenshotFormat='image/jpeg'
        />
    )
}

export default WebCam
