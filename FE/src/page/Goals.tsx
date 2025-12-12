import React, { useEffect, useRef, useState } from 'react'
import SideBar from '../components/SideBar'
import { FaPlus } from "react-icons/fa";
import { CiCalendar } from "react-icons/ci";
import { MdEdit } from "react-icons/md";
import { IoIosNotifications } from "react-icons/io";
import { PiConfetti } from "react-icons/pi";
import { FaPercentage } from "react-icons/fa";
import { FaArrowRight } from "react-icons/fa";
import { instance } from '../api/axios';
import { RiErrorWarningLine } from "react-icons/ri";
import { SiTicktick } from "react-icons/si";

interface Props {
    userid:string
}
interface Goal{
  _id:string
  title:string,
  description:string,
  date:string,
  current_progress:number,
  status:string
}
const Goals = ({userid}:Props) => {
  const dummy = {
    _id:'',
  title:'',
  description:'',
  date:'',
  current_progress:0,
  status:''
  }
  const updater_progress_ref = useRef<HTMLInputElement | null>(null)
  const updater_old_progress_ref = useRef<HTMLInputElement | null>(null)
  const goal_title_ref = useRef<HTMLInputElement | null>(null)
  const goal_desc_ref = useRef<HTMLInputElement | null>(null)
  const goal_date_ref = useRef<HTMLInputElement | null>(null)
  const updater_ref = useRef<HTMLDivElement | null>(null)
  const creater_ref = useRef<HTMLDivElement | null>(null)
  const [isUpdate, setisUpdate] = useState<boolean>(false)
  const [isCreate, setisCreate] = useState<boolean>(false)
  const [currentGoal,setcurrentGoal] = useState<Goal>(dummy)
  const [Goals,setGoals] = useState<Goal[]>()
  const [sortState,setSortState] = useState<string>("")
  const [GoalsConstant,setGoalsConstant] = useState<Goal[]>()
  const handle_sort_type = (type:string) =>{
    setSortState(type)
    if(Goals){
      setGoalsConstant(Goals.filter(goal => goal.status == type))
    }
  }
  const handle_update_progress = async (_id:string) => {
    if(updater_progress_ref.current){
      const new_progress = Number(updater_progress_ref.current.value)
      const response = await instance.put("/edit_goal_progress", {_id:_id,new_progress:new_progress},{headers: {"Content-Type":'application/json'}})
      get_goals()
      handle_close_updater(dummy)
    }
  }
  const handle_create_goal = async () => {
    if(goal_title_ref.current && goal_desc_ref.current && goal_date_ref.current){
      const title = goal_title_ref.current.value
      const desc = goal_desc_ref.current.value
      const date = goal_date_ref.current.value
      const response = await instance.post("/create_goal",{
        title:title,
        desc:desc,
        deadline:date,
        userid:userid
      },{
        headers: {"Content-Type":'application/json'}
      })
      get_goals()
      handle_close_creater()
    }
  }
  const get_goals = async () =>{
    
    const response = await instance.post("/get_goals",{
        userid:userid 
      },{
        headers: {"Content-Type":'application/json'}
      })
    const data:any[] = response.data
    setGoalsConstant(data)
    if(sortState == ""){
      setGoals(data)
    }else{
      setGoals(data.filter(goal => goal.status == sortState))
    }

    console.log(data)
  }
  const handle_close_updater = (goal:Goal) => {
    setisUpdate(!isUpdate)
    if(goal._id != ""){
      setcurrentGoal(goal)
    } 
    if(updater_progress_ref.current){
      updater_progress_ref.current.value = '' 
    }
  }
  const handle_close_creater = () => {
    setisCreate(!isCreate)
    if(goal_title_ref.current && goal_desc_ref.current && goal_date_ref.current){
      goal_title_ref.current.value = goal_desc_ref.current.value = goal_date_ref.current.value = '' 
    }
  }
  const handle_delete_goal = async (_id:string) =>{
    const response = await fetch(`${import.meta.env.VITE_API_ENDPOINT}/delete_goal`,{
      method:"delete",
      body: JSON.stringify({
        _id:_id
      }),
      headers: {'Content-Type':'application/json'}

    })
    get_goals()
    handle_close_updater(dummy)
  }
  useEffect(()=>{
    get_goals()
  },[])
  useEffect(() => {
    if (updater_ref.current) {
      if (!isUpdate) {
        updater_ref.current.className = updater_ref.current.className + " active"
      } else {
        updater_ref.current.className = "goal-updater"
      }
    }
    if (creater_ref.current) {
      if (!isCreate) {
        creater_ref.current.className = creater_ref.current.className + " active"
      } else {
        creater_ref.current.className = "goal-updater"
      }
    }
    

  }, [isUpdate, isCreate])
  return (
    <>
      <SideBar />
      <div className="goal-updater" ref={updater_ref} id='update-goal'>
        <div className="updater-box">
          <div className="updater-title">
            <h2>{currentGoal.title}</h2>
            <p>{currentGoal.description}</p>
          </div>
          <div className="updater-input-box">
            <div className="updater-input">
              <h3>Current Progress</h3>
              <div className="input-box">
                <input type="text" readOnly value={currentGoal.current_progress} />
                <FaPercentage />
              </div>

            </div>
            <FaArrowRight />
            <div className="updater-input">
              <h3>New Progress</h3>
              <div className="input-box">
                <input type="number" ref={updater_progress_ref} min='0' max='100' />
                <FaPercentage />
              </div>

            </div>
          </div>
          <div className="updater-button">
            <button id='updater-cancel' onClick={()=>handle_close_updater(dummy)}>Cancel</button>
            <button id='updater-delete' onClick={()=> handle_delete_goal(currentGoal._id)}>Delete Goal</button>
            <button id='updater-save' onClick={()=>handle_update_progress(currentGoal._id)}>Save Progress</button>
            
          </div>
        </div>
      </div>
      <div className="goal-updater" ref={creater_ref} id='new-goal'>
        <div className="updater-box">
          <div className="updater-title">
            <h2>Update Goal Progress</h2>
            <p>Master Calculus Concepts</p>
          </div>
          <div className="updater-input-box">
            <div className="updater-input">
              <h3>Goal's Title</h3>
              <div className="input-box">
                <input type="text" ref={goal_title_ref} placeholder='e.g Master Calculus Concepts' />
              </div>

            </div>
            <div className="updater-input">
              <h3>Goals' Description</h3>
              <div className="input-box">
                <input type="text" ref={goal_desc_ref} placeholder='e.g Complete all modules on Khan Academy' />
              </div>
            </div>
            <div className="updater-input">
              <h3>Deadline Date</h3>
              <div className="input-box">
                <input type="date" ref={goal_date_ref} />
              </div>
            </div>
          </div>
          <div className="updater-button">
            <button id='updater-cancel' onClick={handle_close_creater}>Cancel</button>
            <button id='updater-save' onClick={handle_create_goal}>Save Progress</button>
            
          </div>
        </div>
      </div>
      <div className="goal">


        {/* header */}

        <div className="goal-header">
          <div className="goal-title">
            <h1>Study Goals</h1>
            <p>Set, track, and conquer your academic objectives</p>
          </div>
          <button className='goal-new-button' onClick={handle_close_creater}><FaPlus /> New Goal</button>
        </div>

        {/* category */}

        <div className="goal-category">
          <p onClick={()=>handle_sort_type("In Progress")} className={sortState == 'In Progress' ? 'active' :''}>In Progress</p>
          <p onClick={()=>handle_sort_type("Completed")} className={sortState == 'Completed' ? 'active' :''}>Completed</p>
          <p onClick={()=>handle_sort_type("Overdue")} className={sortState == 'Overdue' ? 'active' :''}>Overdue</p>
        </div>

        {/* body */}

        <div className="goal-body">
          <div className="goal-container">

            {GoalsConstant?.map((goal)=>{
              let width_style = {"width":`${goal.current_progress}%`}
              
              let classname = goal.status =='Overdue' ? 'goal-card overdue' : (goal.status !='In Progress' ? 'goal-card completed' : 'goal-card') 
              return (
              <div className={classname} key={goal._id}>
              <div className="goal-card-desc">
                <div className="goal-card-title">
                  <h3>{goal.title}</h3>
                  <p>{goal.description}</p>
                </div>
                {goal.status != 'Overdue'
                 ?
                 ( goal.status != 'In Progress'
                  ?
                 <p className='goal-card-deadline'><SiTicktick /> Goal Completed </p>
                 :
                 <p className='goal-card-deadline'><CiCalendar /> Due Oct 31 </p>
                )
                  :
                  (
                    <p className='goal-card-deadline'><RiErrorWarningLine /> Overdue </p>
                  )
                  
                 }
                
              </div>
              <div className="goal-card-progression">
                <div className="progress-bar"><span style={width_style}></span></div>
                <p className='progress-percent'>{goal.current_progress}%</p>
                <button className='progress-edit' onClick={()=> {handle_close_updater(goal)}}><MdEdit /></button>
              </div>
            </div>
              )
            })

            }
            

          </div>
          <div className="goal-extra">
            <div className="goal-summary">
              <div className="goal-summary-title">
                <h2>Goal Summary</h2>
              </div>
              <div className="goal-statistic">
                <h3>Active Goals</h3>
                <p>{Goals?.length}</p>
              </div>
              <div className="goal-statistic">
                <h3>Completed</h3>
                <p>{Goals?.filter(goal => goal.status == 'Completed').length}</p>
              </div>
              <div className="goal-statistic">
                <h3>Overall Progress</h3>
                {Goals ?  <p className="progress-text">{Goals?.length ? Math.floor(Goals?.filter(goal => goal.status == 'Completed').length*100/Goals?.length) : 0}%</p> : ''}
               
              </div>
            </div>
            <div className="goal-notification">
              <h2>Notification</h2>
              <div className="goal-warning">
                <IoIosNotifications />
                <div className="noti-desc">
                  <h3>Deadline approching</h3>
                  <h4>'Master Calculus' is due in 3 days</h4>

                </div>
              </div>
              <div className="goal-completed">
                <PiConfetti />
                <div className="noti-desc">
                  <h3>Goal achieved!</h3>
                  <h4>You completed 'Write History Essay'</h4>
                </div>
              </div>
            </div>
          </div>

        </div>


      </div>
    </>
  )
}

export default Goals