import React, { type JSX } from 'react'
import { useAuth } from '../hooks/useAuth'
import { Navigate } from 'react-router-dom'

const ProtectedRoute = ({children}: {children: React.ReactElement }) => {
    const {isSignedIn, logout, userid} = useAuth()
    if(!isSignedIn){
        return <Navigate to="/signin"/>
    }
  return React.cloneElement(children,userid);
}

export default ProtectedRoute