let app = new Vue({
    el: "#container",
    delimiters: ['[[', ']]'],
    data: {
        tasks: [],
        form: {
            url: "",
        },
    },

    created: function(){
        this.getTasks();
    },

    mounted: function(){},

    methods: {
        getTasks: function(){
            axios.get("/api/tasks/", {})
            .then((response) => {
                if (response.status === 200){
                    this.tasks = response.data;
                }else{
                    this.$message.error(response.data);
                }
            }).catch(error => {
                this.$message.error(error.response.data.message);
            });
        },

        onSubmit: function(){
            axios.post("/api/tasks/", this.form).then((response) => {
                console.log(response);
            });
        },
    },

    watch: {},
});
