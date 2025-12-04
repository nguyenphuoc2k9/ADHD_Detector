import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import AppRoutes from './routes/AppRoutes'
import SideBar from './components/SideBar'
function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div className='content-box'>
        
        <AppRoutes userid='692f03cf6f92de6a879a0528'/>
      </div>
      <div></div>
    </>
   
  )
}

export default App
