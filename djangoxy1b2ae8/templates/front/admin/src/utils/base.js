const base = {
    get() {
        return {
            url : "http://localhost:8080/djangoxy1b2ae8/",
            name: "djangoxy1b2ae8",
            // 退出到首页链接
            indexUrl: ''
        };
    },
    getProjectName(){
        return {
            projectName: "基于ECharts的海洋气象数据可视化平台设计与实现"
        } 
    }
}
export default base
