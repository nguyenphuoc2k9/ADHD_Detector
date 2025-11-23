import React, { useRef, useState } from 'react'
import { MdOutlineSchool } from "react-icons/md";
import { NavLink } from "react-router-dom"
import "./style.css"
import { MdOutlineDashboard } from "react-icons/md";
import { RiTodoLine } from "react-icons/ri";
import { IoBookOutline } from "react-icons/io5";
import { CiSettings } from "react-icons/ci";
import { CgProfile } from "react-icons/cg";

const SideBar = () => {
    const [active,setActive] = useState<string>("")
    const handleActive = ()=>{
        if(active == ""){
            setActive(" active")
        }else{
            setActive("")
        }
        console.log(active)
    }
    
    return (
        <div className={"sidebar"+active}>
            <div className="welcome-box">
                <MdOutlineSchool onClick={handleActive}/>
                <div className="welcome-text">
                    <h3>StudyTrack</h3>
                    <p>Welcome Back!</p>
                </div>

            </div>
            <div className="page-box">
                <div className="page-card">
                    <NavLink to="/" className={({ isActive, isPending }) => isActive ? "active" : ""}><MdOutlineDashboard /><p>Dashboard</p></NavLink>
                </div>
                <div className="page-card">
                    <NavLink to="/goals" className={({ isActive, isPending }) => isActive ? "active" : ""}><RiTodoLine /><p>Goals</p></NavLink>

                </div>
                <div className="page-card">
                    <NavLink to="/studypage" className={({ isActive, isPending }) => isActive ? "active" : ""}><IoBookOutline /><p>StudyPage</p></NavLink>

                </div>


            </div>
            <div className="setting-box">
                <div className='page-card'>

                    <NavLink to="/setting" className={({ isActive, isPending }) => isActive ? "active" : ""}><CiSettings /><p>Settings</p></NavLink>
                </div>
                <div className='page-card'>

                    <NavLink to="/profile" className={({ isActive, isPending }) => isActive ? "active" : ""}><CgProfile /><p>Profile</p></NavLink>
                </div>


            </div>
        </div>
    )
}

export default SideBar