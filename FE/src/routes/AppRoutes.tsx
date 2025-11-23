import {createBrowserRouter,RouterProvider} from "react-router-dom"
import Home from "../page/Home"
import About from "../page/About"
import UserProfile from "../page/UserProfile"
import NotFound from "../page/NotFound"
import Registry from "../page/Registry"
import Login from "../page/Login"
import Goals from "../page/Goals"
import StudyPage from "../page/StudyPage"
const router = createBrowserRouter([
    {
        path:"/",
        element:<Home/>
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
        element:<Goals/>
    },
    {
        path:"/studypage",
        element:<StudyPage/>
    }
])
export default function AppRoutes(){
    return <RouterProvider router={router}/>
}