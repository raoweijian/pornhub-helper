let app = new Vue({
    el: "#container",
    delimiters: ['[[', ']]'],
    data: {
        tasks: [],
        curPage: 1,
        taskCount: 0,
        pageSize: 10,
        form: {
            url: "",
        },
        timer: 0,
    },

    created: function(){
        this.getTasks();
    },

    mounted: function(){
        this.timer = setInterval(this.getTasks, 5000);
    },

    methods: {
        /**
         * 获取任务列表
         */
        getTasks: function(){
            let url = "/api/tasks/?page=" + this.curPage;
            axios.get(url, {}).then((response) => {
                if (response.status === 200){
                    this.tasks = response.data.data;
                    this.curPage = response.data.cur_page;
                    this.pageSize = response.data.page_size;
                    this.taskCount = response.data.task_count;
                }else{
                    this.$message.error(response.data);
                }
            }).catch(error => {
                this.$message.error(error.response.data.message);
            });
        },

        /**
         * 提交下载
         */
        onSubmit: function(){
            axios.post("/api/tasks/", this.form).then((response) => {
                this.getTasks();
            });
        },

        /**
         * 切换分页
         */
        pageSwitch: function(val){
            this.curPage = val;
        },

        /**
         * 勾选一条内容，表示已经下载
         */
        check: function(taskId){
            let url = "/api/tasks/" + taskId;
            axios.put(url, {
                "status": -2,
            }).then((response) => {
                if (response.status === 200){
                    this.getTasks();
                }else{
                    this.$message.error(response.data);
                }   
            }).catch(error => {
                this.$message.error(error.response.data.message);
            }); 
        },
    },

    watch: {
        curPage: function(newVal, oldVal){
            this.getTasks();
        }
    },
});
