<template>
    <div>
        <v-row>
            <v-col cols="10">
                <v-text-field
                        v-model="frequency"
                        label="Update Frequency"
                        type="number"
                ></v-text-field>

            </v-col>
            <v-col>
                <v-btn rounded color="deep-purple accent-4" dark v-on:click="setUpdateFrequency">Submit</v-btn>
            </v-col>
        </v-row>

        <v-divider></v-divider>

        <v-tabs
                background-color="deep-purple accent-4"
                class="elevation-2"
                dark
                centered
        >
            <v-tabs-slider></v-tabs-slider>

            <v-tab
                    v-for="(item, i) in prices"
                    :key="i"
                    :href="`#tab-${i}`"
            >
                {{ item.symbol }}
            </v-tab>

            <v-tab-item
                    v-for="(item, i) in prices"
                    :key="i"
                    :value="'tab-' + i"
            >
                <v-card
                        flat
                        tile
                >
                    <v-card-text>

                        <v-sheet
                                class="v-sheet--offset mx-auto"
                        >
                            <v-sparkline
                                    :value="item.valueList.slice(0,60)"
                                    color="deep-purple accent-4"
                                    line-width="0.3"
                                    :smooth="16"
                                    max-height="200px"
                            ></v-sparkline>
                        </v-sheet>

                        <v-divider></v-divider>


                        <v-text-field
                                v-model="item.benchmark"
                                label="Benchmark Price"
                        ></v-text-field>

                        <v-spacer></v-spacer>

                        <v-subheader>PRICES</v-subheader>
                        <ol>
                            <li
                                    v-for="(value, j) in item.valueList.slice(0,item.length)"
                                    :key="j"
                                    :class="{'positive': value>item.benchmark, 'negative': value<item.benchmark }"
                            >
                                <span v-text="value"></span>
                            </li>
                        </ol>

                        <v-btn outlined color="deep-purple" v-on:click="item.length= item.length===100?500:100">Show {{item.length===100?'more':'less'}}</v-btn>

                    </v-card-text>
                </v-card>
            </v-tab-item>
        </v-tabs>

        <v-snackbar
                v-model="snackbar.open"
        >
            {{ snackbar.text }}
            <v-btn
                    color="red"
                    text
                    @click="snackbar.open = false"
            >
                Close
            </v-btn>
        </v-snackbar>

    </div>
</template>

<style>
    .positive {
        background-color: #c1ffa8;
    }

    .negative {
        background-color: #ffa8a8;
    }
</style>

<script>
    export default {
        name: 'Price',

        data: () => ({
            snackbar:{
                open: false,
                text: "ok"
            },
            websocket: null,
            frequency: 300,
            prices: [
                {
                    "symbol": "AAAA",
                    "benchmark": 105,
                    "length":100,
                    "valueList": []
                }, {
                    "symbol": "BBBB",
                    "benchmark": 105,
                    "length":100,
                    "valueList": []
                }, {
                    "symbol": "CCCC",
                    "benchmark": 105,
                    "length":100,
                    "valueList": []
                }, {
                    "symbol": "DDDD",
                    "benchmark": 105,
                    "length":100,
                    "valueList": []
                }

            ]
        }),
        created: function () {
            this.websocket = new WebSocket("ws://127.0.0.1:5678/");
            // setInterval(() => {
            //     this.prices[0].valueList.unshift(Math.floor(Math.random() * 10));
            //     if (this.prices[0].valueList.length > 500) {
            //         this.prices[0].valueList.pop();
            //     }
            // }, 500)
            let pricelistObj = this.prices;
            let snackObj = this.snackbar;
            this.websocket.onmessage = function (event) {
                const data = JSON.parse(event.data);
                if(data.type==='notice'){
                    snackObj.open=true;
                    snackObj.text="frequency updated to " + data.msg + "ms"
                }else{
                    data.forEach(item => {
                        pricelistObj.forEach(element =>{
                            if(element.symbol === item.symbol){
                                element.valueList.unshift(item.price);
                                if (element.valueList.length > 500){
                                    element.valueList.pop();
                                }
                            }
                        })
                    })
                }
            };
        },
        methods: {
            setUpdateFrequency: function () {
                this.websocket.send(JSON.stringify({frequency: parseInt(this.frequency)}));
            }
        }
    };
</script>
