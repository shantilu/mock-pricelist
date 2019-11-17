<template>
    <div>
        <v-card-text>
        <v-row>
            <v-col cols="10">
                <v-text-field
                        v-model="frequency"
                        label="Update Frequency"
                        type="number"
                ></v-text-field>

            </v-col>
            <v-col>
                <v-btn outlined color="indigo" dark v-on:click="setUpdateFrequency">Submit</v-btn>
            </v-col>
        </v-row>
        </v-card-text>

        <v-tabs
                fixed-tabs
                background-color="indigo"
                dark
        >
            <v-tab href="#tab0">
                Price Update
            </v-tab>
            <v-tab href="#tab1">
                Query history
            </v-tab>

            <v-tab-item value="tab0" id="tab0">
                <v-card>
                    <div>
                        <v-row align="center">
                            <v-col class="d-flex" cols="12" sm="6">
                                <v-text-field
                                        v-model="benchmark"
                                        label="Benchmark Price"
                                ></v-text-field>
                            </v-col>

                            <v-col class="d-flex" cols="12" sm="6">
                                <v-select
                                        v-model="symbolFilter"
                                        :items="symbols"
                                        label="filter by symbol"
                                ></v-select>
                            </v-col>
                        </v-row>

                        <v-divider></v-divider>



                        <v-simple-table
                                dense
                                fixed-header
                        >
                            <template v-slot:default>
                                <thead>
                                <tr>
                                    <th>Display Sequence</th>
                                    <th class="text-left">Symbol</th>
                                    <th class="text-left">Price</th>
                                    <th>Timestamp</th>
                                </tr>
                                </thead>
                                <tbody>
                                <tr v-for="(item, index) in prices.filter(item=>(item.symbol===symbolFilter)||(symbolFilter==='')).slice(0, displayLength)" :key="index"
                                    :class="{'positive': item.price>benchmark, 'negative': item.price<benchmark }">
                                    <td>{{index+1}}</td>
                                    <td>{{ item.symbol }}</td>
                                    <td>{{ item.price }}</td>
                                    <td>{{ item.time }}</td>
                                </tr>
                                </tbody>
                            </template>
                        </v-simple-table>

                        <v-spacer></v-spacer>
                        <div class="my-3">
                            <v-btn outlined color="indigo" v-on:click="displayLength= displayLength===100?500:100">Show {{displayLength===100?'more':'less'}}</v-btn>
                        </div>


                    </div>
                </v-card>
            </v-tab-item>

            <v-tab-item value="tab1" id="tab1">
                <v-card>
                    <v-subheader>Select time range in seconds delta from now</v-subheader>
                    <v-card-text>
                        <v-range-slider
                                v-model="queryRange"
                                max=0
                                min=-300
                                thumb-label="always"
                        ></v-range-slider>
                        <v-btn outlined color="deep-purple accent-4" dark v-on:click="queryTimeRange">Submit</v-btn>

                    </v-card-text>

                    <v-simple-table
                            dense
                            fixed-header
                            v-if="queryResult.length"
                    >
                        <template>
                            <thead>
                            <tr>
                                <th>Display Sequence</th>
                                <th class="text-left">Symbol</th>
                                <th class="text-left">Price</th>
                                <th>Timestamp</th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr v-for="(item, index) in queryResult" :key="index"
                                :class="{'positive': item.price>benchmark, 'negative': item.price<benchmark }">
                                <td>{{index+1}}</td>
                                <td>{{ item.symbol }}</td>
                                <td>{{ item.price }}</td>
                                <td>{{ item.time }}</td>
                            </tr>
                            </tbody>
                        </template>
                    </v-simple-table>

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

<script>
    export default {
        name: "PriceUpdate",

        data: () => ({
            snackbar: {
                open: false,
                text: "ok"
            },
            websocket: null,
            benchmark: 105,
            frequency: 300,
            displayLength: 100,
            prices: [],
            symbols: [''],
            symbolFilter: '',
            queryResult:[],
            queryRange:[-120, -60]
        }),
        created: function () {
            this.websocket = new WebSocket("ws://127.0.0.1:5678/");

            let snackObj = this.snackbar;
            let myObj = this;

            this.websocket.onmessage = function (event) {
                const data = JSON.parse(event.data);
                if (data.type === 'notice') {
                    snackObj.open = true;
                    snackObj.text = "frequency updated to " + data.msg + "ms"
                } else if (data.type === 'query') {
                    myObj.queryResult = data.data;
                } else {
                    data.forEach(item => {
                        if (myObj.symbols.indexOf(item.symbol) < 0) {
                            myObj.symbols.push(item.symbol)
                        }
                        myObj.prices.unshift(item);
                        if (myObj.prices.length > 500) {
                            myObj.prices.pop();
                        }
                    })
                }
            };
        },
        methods: {
            setUpdateFrequency: function () {
                const updated = parseInt(this.frequency);
                if (updated<100){
                    alert("frequency less than 100 is not supported");
                    return
                }
                this.websocket.send(JSON.stringify({frequency: updated}));
            },
            queryTimeRange: function () {
                this.websocket.send(JSON.stringify({range: this.queryRange}));
            }
        }
    }
</script>

<style scoped>
    .positive {
        background-color: #c1ffa8;
    }

    .negative {
        background-color: #ffa8a8;
    }
</style>
