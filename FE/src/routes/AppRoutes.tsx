import {createBrowserRouter,RouterProvider} from "react-router-dom"
import Home from "../page/Home"
import About from "../page/About"
import UserProfile from "../page/UserProfile"
import NotFound from "../page/NotFound"
import Registry from "../page/Registry"
import Login from "../page/Login"
import Goals from "../page/Goals"
import StudyPage from "../page/StudyPage"
interface Props {
    userid:string
}
export default function AppRoutes({userid}:Props){
    const router = createBrowserRouter([
    {
        path:"/",
        element:<Home userid={userid}/>
    },
    {
        path:"/about",
        element:<About/>
    },
    {
        path:"/user/:id",
        element:<UserProfile/>
    },
    {
        path:"*",
        element:<NotFound/>
    },
    {
        path:"/registry",
        element:<Registry/>
    },
    {
        path:"/login",
        element:<Login/>
    },
    {
        path:"/goals",
        element:<Goals userid={userid}/>
    },
    {
        path:"/studypage",
        element:<StudyPage userid={userid}/>
    }
])
    return <RouterProvider router={router}/>
}