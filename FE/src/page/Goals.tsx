import React from 'react'
import SideBar from '../components/SideBar'
import { FaPlus } from "react-icons/fa";
import { CiCalendar } from "react-icons/ci";
import { MdEdit } from "react-icons/md";

const Goals = () => {
  
  return (
    <>
      <SideBar />
      <div className="goal">

        {/* header */}

        <div className="goal-header">
          <div className="goal-title">
            <h1>Study Goals</h1>
            <p>Set, track, and conquer your academic objectives</p>
          </div>
            <button className='goal-new-button'><FaPlus /> New Goal</button>
        </div>

        {/* category */}

        <div className="goal-category">
          <p>In Progress</p>
          <p>completed</p>
          <p>Overdue</p>
        </div>

        {/* body */}

        <div className="goal-body">
          <div className="goal-container">
            <div className="goal-card">
                <div className="goal-card-desc">
                  <div className="goal-card-title">
                    <h3>Master CalCulus Concepts</h3>
                    <p>Complete all modules on Khan Academy</p>
                  </div>
                    <p className='goal-card-deadline'> <CiCalendar/> Due Oct 31</p>
                </div>
                <div className="goal-card-progression">
                  <div className="progress-bar"><span></span></div>
                  <p className='progress-percent'>75%</p>
                  <button className='progress-edit'><MdEdit/></button>
                </div>
            </div>
            <div className="goal-card">
                <div className="goal-card-desc">
                  <div className="goal-card-title">
                    <h3>Master CalCulus Concepts</h3>
                    <p>Complete all modules on Khan Academy</p>
                  </div>
                    <p className='goal-card-deadline'> <CiCalendar/> Due Oct 31</p>
                </div>
                <div className="goal-card-progression">
                  <div className="progress-bar"><span></span></div>
                  <p className='progress-percent'>75%</p>
                  <button className='progress-edit'><MdEdit/></button>
                </div>
            </div>
            <div className="goal-card">
                <div className="goal-card-desc">
                  <div className="goal-card-title">
                    <h3>Master CalCulus Concepts</h3>
                    <p>Complete all modules on Khan Academy</p>
                  </div>
                    <p className='goal-card-deadline'> <CiCalendar/> Due Oct 31</p>
                </div>
                <div className="goal-card-progression">
                  <div className="progress-bar"><span></span></div>
                  <p className='progress-percent'>75%</p>
                  <button className='progress-edit'><MdEdit/></button>
                </div>
            </div>
            <div className="goal-card">
                <div className="goal-card-desc">
                  <div className="goal-card-title">
                    <h3>Master CalCulus Concepts</h3>
                    <p>Complete all modules on Khan Academy</p>
                  </div>
                    <p className='goal-card-deadline'> <CiCalendar/> Due Oct 31</p>
                </div>
                <div className="goal-card-progression">
                  <div className="progress-bar"><span></span></div>
                  <p className='progress-percent'>75%</p>
                  <button className='progress-edit'><MdEdit/></button>
                </div>
            </div>
            <div className="goal-card">
                <div className="goal-card-desc">
                  <div className="goal-card-title">
                    <h3>Master CalCulus Concepts</h3>
                    <p>Complete all modules on Khan Academy</p>
                  </div>
                    <p className='goal-card-deadline'> <CiCalendar/> Due Oct 31</p>
                </div>
                <div className="goal-card-progression">
                  <div className="progress-bar"><span></span></div>
                  <p className='progress-percent'>75%</p>
                  <button className='progress-edit'><MdEdit/></button>
                </div>
            </div>
            <div className="goal-card">
                <div className="goal-card-desc">
                  <div className="goal-card-title">
                    <h3>Master CalCulus Concepts</h3>
                    <p>Complete all modules on Khan Academy</p>
                  </div>
                    <p className='goal-card-deadline'> <CiCalendar/> Due Oct 31</p>
                </div>
                <div className="goal-card-progression">
                  <div className="progress-bar"><span></span></div>
                  <p className='progress-percent'>75%</p>
                  <button className='progress-edit'><MdEdit/></button>
                </div>
            </div>
            <div className="goal-card">
                <div className="goal-card-desc">
                  <div className="goal-card-title">
                    <h3>Master CalCulus Concepts</h3>
                    <p>Complete all modules on Khan Academy</p>
                  </div>
                    <p className='goal-card-deadline'> <CiCalendar/> Due Oct 31</p>
                </div>
                <div className="goal-card-progression">
                  <div className="progress-bar"><span></span></div>
                  <p className='progress-percent'>75%</p>
                  <button className='progress-edit'><MdEdit/></button>
                </div>
            </div>
            <div className="goal-card">
                <div className="goal-card-desc">
                  <div className="goal-card-title">
                    <h3>Master CalCulus Concepts</h3>
                    <p>Complete all modules on Khan Academy</p>
                  </div>
                    <p className='goal-card-deadline'> <CiCalendar/> Due Oct 31</p>
                </div>
                <div className="goal-card-progression">
                  <div className="progress-bar"><span></span></div>
                  <p className='progress-percent'>75%</p>
                  <button className='progress-edit'><MdEdit/></button>
                </div>
            </div>
            <div className="goal-card">
                <div className="goal-card-desc">
                  <div className="goal-card-title">
                    <h3>Master CalCulus Concepts</h3>
                    <p>Complete all modules on Khan Academy</p>
                  </div>
                    <p className='goal-card-deadline'> <CiCalendar/> Due Oct 31</p>
                </div>
                <div className="goal-card-progression">
                  <div className="progress-bar"><span></span></div>
                  <p className='progress-percent'>75%</p>
                  <button className='progress-edit'><MdEdit/></button>
                </div>
            </div>
            <div className="goal-card">
                <div className="goal-card-desc">
                  <div className="goal-card-title">
                    <h3>Master CalCulus Concepts</h3>
                    <p>Complete all modules on Khan Academy</p>
                  </div>
                    <p className='goal-card-deadline'> <CiCalendar/> Due Oct 31</p>
                </div>
                <div className="goal-card-progression">
                  <div className="progress-bar"><span></span></div>
                  <p className='progress-percent'>75%</p>
                  <button className='progress-edit'><MdEdit/></button>
                </div>
            </div>
            <div className="goal-card">
                <div className="goal-card-desc">
                  <div className="goal-card-title">
                    <h3>Master CalCulus Concepts</h3>
                    <p>Complete all modules on Khan Academy</p>
                  </div>
                    <p className='goal-card-deadline'> <CiCalendar/> Due Oct 31</p>
                </div>
                <div className="goal-card-progression">
                  <div className="progress-bar"><span></span></div>
                  <p className='progress-percent'>75%</p>
                  <button className='progress-edit'><MdEdit/></button>
                </div>
            </div>
            
          </div>
          <div className="goal-extra">
            <div className="goal-summary">

            </div>
            <div className="goal-notifications">

            </div>
          </div>

        </div>


      </div>
    </>
  )
}

export default Goals