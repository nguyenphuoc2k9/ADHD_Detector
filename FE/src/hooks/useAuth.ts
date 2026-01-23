export const useAuth = ()=>{
    const userid = localStorage.getItem("userid")
    return {
        isSignedIn: !!userid,
        userid : userid ? JSON.parse(userid) : null,
        logout: () =>{
            localStorage.removeItem("userid")
            globalThis.location.reload();
        }
    }
}