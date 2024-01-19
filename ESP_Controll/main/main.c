/* Includes ***************************************************************/
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/timers.h"
#include "driver/gpio.h"
#include "esp_sleep.h"
#include "esp_intr_alloc.h"

#define LOG_LOCAL_LEVEL ESP_LOG_VERBOSE
#include "esp_log.h"
#include "esp_timer.h"


#include "../components/libHanDi/include/device/adc.h"
#include "../components/libHanDi/include/energyunit.h"
#include "../components/libHanDi/include/delay.h"
//TODO: Create sample Tasks( Computation Idle Measure Send Data)
//TODO: Measure Udrop. 

/* Private defines ********************************************************/
static const char* TAG = "MAIN";

#define TIMEOUT_TASK_us 10000

#define VOLTAGE_DROP_MEASUREMENT
//#define VOLTAGE_MEASUREMENT

// GPIOs
#define GPIO_SYNC_SIG GPIO_NUM_3
#define GPIO_CHARGE GPIO_NUM_6
#define GPIO_POWER_ON GPIO_NUM_7

/* Private constants ******************************************************/
const TickType_t tt_Delay_ms = pdMS_TO_TICKS(2); 
const TickType_t chargingTime_ms = pdMS_TO_TICKS(2000);
/* Private macros *********************************************************/

/* Private typedefs *******************************************************/

/* Private function prototypes ********************************************/
void sendGPIOPulseBlocking(uint16_t us_duration_ms);


/* Private variables ******************************************************/
TimerHandle_t xTimer1;


gpio_isr_handle_t syncISRHandle;

volatile bool syncSignal =false;

/* Public functions *******************************************************/

/* Private functions ******************************************************/
void measure_adc();
void measure_voltagedrop();
void isrSynchandker(void *arg){
    syncSignal = true;
}

void app_main(void)
{   
    esp_log_level_set(TAG, ESP_LOG_INFO);

    
    


    #if defined(VOLTAGE_DROP_MEASUREMENT)

    energyunit_init();
    measure_voltagedrop();
    
    #elif defined(VOLTAGE_MEASUREMENT)

    continuous_adc_init();
    measure_adc();

    #endif
    

}


void measure_adc()
{
    gpio_set_direction(GPIO_NUM_3, GPIO_MODE_OUTPUT); // GPIO for state signaling
    gpio_set_level(GPIO_NUM_3, 1);
    int voltage = 3;
    bool ok = false; 
    for(int i = 0 ; i <800;i++)
    {
        gpio_set_level(GPIO_NUM_3, 1);
        vTaskDelay(pdMS_TO_TICKS(10));
        ok = adc_measure_raw(&voltage);
        gpio_set_level(GPIO_NUM_3, 0);
        printf("Measurement OK: %i Voltage mV: %i \n",ok, voltage);       
        vTaskDelay(pdMS_TO_TICKS(50));
    }

}

void sendSyncSignal()
{

}
void measure_voltagedrop()
{
    esp_log_level_set(TAG, ESP_LOG_INFO);
    uint32_t startVoltage_mV; 
    uint32_t finalVoltage_mV;
    uint32_t measuredVoltage_mV;
    uint32_t minVoltage_mV;
    uint16_t nMeasurements;
    uint16_t nStartVMeasurements;
    //Initialize GPIOs
   

    gpio_set_direction(GPIO_CHARGE, GPIO_MODE_OUTPUT);
    gpio_set_direction(GPIO_POWER_ON, GPIO_MODE_OUTPUT);


    // Set up interrupt
    gpio_set_direction(GPIO_SYNC_SIG, GPIO_MODE_INPUT); // GPIO for state signaling
    gpio_set_pull_mode(GPIO_SYNC_SIG, GPIO_PULLDOWN_ONLY);
    gpio_set_intr_type(GPIO_SYNC_SIG, GPIO_INTR_POSEDGE);
    //gpio_install_isr_service(ESP_INTR_FLAG_NMI);
    
    gpio_isr_handler_add(GPIO_SYNC_SIG, isrSynchandker, NULL);

    // Measure total evaluation time 
    int64_t startTimeEval = esp_timer_get_time();
    for(int i = 0 ; i <100; i++)
    {

        // Reset values
        startVoltage_mV = 0; 
        finalVoltage_mV = 0;
        measuredVoltage_mV = UINT32_MAX;
        minVoltage_mV = UINT32_MAX;
        nMeasurements = 0;
        nStartVMeasurements = 0;
        

        // Charge Caps
        ESP_LOGI(TAG, "Measurement %i - Charging Caps...", i);
        gpio_set_level(GPIO_POWER_ON,0);
        gpio_set_level(GPIO_CHARGE,1);
        vTaskDelay(chargingTime_ms);
        gpio_set_level(GPIO_CHARGE,0);

        // Power ESP on
        gpio_set_level(GPIO_POWER_ON,1);

        syncSignal = false; 
        startVoltage_mV = energyunit_measureVoltage();

        // Wait for start signal  
        //ESP_LOGD(TAG, "Waiting for signal...");
        while(!syncSignal)
        {
            startVoltage_mV = energyunit_measureVoltage();
            nStartVMeasurements++;
        }
        syncSignal = false; 
        ESP_LOGD(TAG, "N StartV: %u",  nStartVMeasurements); 
        // Measure starting conditions
        delay(210);
        int64_t startTimeTask = esp_timer_get_time();
        
        ESP_LOGD(TAG, "Initial Voltage: %lu mV",  startVoltage_mV); 
        
        

        while(!syncSignal)
        {
            // Measure minimal voltage for voltage drop
            uint32_t measuredVoltage_mV = energyunit_measureVoltage();
            if(measuredVoltage_mV<minVoltage_mV)
            {
                minVoltage_mV = measuredVoltage_mV;
            }
            nMeasurements++;
        }
        syncSignal = false;
        
        
        
        finalVoltage_mV = energyunit_measureVoltage();
        int errCnt = 0;
        int64_t startMeasureFinalV = esp_timer_get_time();
        while(esp_timer_get_time()-startMeasureFinalV < 25000)
        {
            measuredVoltage_mV = energyunit_measureVoltage();
            if(measuredVoltage_mV > finalVoltage_mV)
            {
                finalVoltage_mV = measuredVoltage_mV;
            }
            
        }
        
        ESP_LOGD(TAG, "Number of Measurements during execution: %u",nMeasurements);
        uint32_t voltageDrop_mV = 0;
        if(minVoltage_mV<=finalVoltage_mV && startVoltage_mV>=finalVoltage_mV) {
            voltageDrop_mV = finalVoltage_mV - minVoltage_mV;
            printf("Start Voltage: %lu mV\n", startVoltage_mV); 
            printf("Final Voltage: %lu mV\n", finalVoltage_mV); 
            printf("Voltage Drop: %lu mV\n", voltageDrop_mV); 
        }
        else if (finalVoltage_mV<minVoltage_mV)
        {
            ESP_LOGW(TAG, "Min Voltage: %lu final Voltage: %lu", minVoltage_mV, finalVoltage_mV); 
            i--;
        }
        else if (startVoltage_mV<finalVoltage_mV)
        {
            //ESP_LOGW(TAG, "Start voltage: %lu - final Voltage: %lu",startVoltage_mV, finalVoltage_mV); 
            i--;
        }
        
    }
    int64_t taskTime_us = esp_timer_get_time() - startTimeEval;
    ESP_LOGI(TAG, "Measurement complete after: %lli s", taskTime_us/1000000); 
}


