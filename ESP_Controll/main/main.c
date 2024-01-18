/* Includes ***************************************************************/
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/timers.h"
#include "driver/gpio.h"
#include "esp_sleep.h"

#define LOG_LOCAL_LEVEL ESP_LOG_VERBOSE
#include "esp_log.h"
#include "esp_timer.h"

#include "../components/libHanDi/include/device/adc.h"
#include "../components/libHanDi/include/energyunit.h"
//TODO: Create sample Tasks( Computation Idle Measure Send Data)
//TODO: Measure Udrop. 

/* Private defines ********************************************************/
static const char* TAG = "MAIN";



#define VOLTAGE_DROP_MEASUREMENT
//#define VOLTAGE_MEASUREMENT

// GPIOs
#define GPIO_SYNC_SIG GPIO_NUM_3
#define GPIO_CHARGE GPIO_NUM_6
#define GPIO_POWER_ON GPIO_NUM_7

/* Private constants ******************************************************/
const TickType_t tt_Delay_ms = pdMS_TO_TICKS(3); 
const TickType_t chargingTime_ms = pdMS_TO_TICKS(16000);
/* Private macros *********************************************************/

/* Private typedefs *******************************************************/

/* Private function prototypes ********************************************/
void sendGPIOPulseBlocking(uint16_t us_duration_ms);


/* Private variables ******************************************************/
TimerHandle_t xTimer1;
uint32_t minVoltage_mV = UINT32_MAX;
uint32_t dropVoltage_mV = UINT32_MAX;

/* Public functions *******************************************************/

/* Private functions ******************************************************/
void measure_adc();
void measure_voltagedrop();
bool prv_createSWTimer(void);
bool prv_startSWTimer(void);

void app_main(void)
{   
    esp_log_level_set(TAG, ESP_LOG_INFO);
    


    #if defined(VOLTAGE_DROP_MEASUREMENT)

    energyunit_init();
    prv_createSWTimer();
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

void measure_voltagedrop()
{
    esp_log_level_set(TAG, ESP_LOG_INFO);
    uint32_t startVoltage_mV = 0; 
    uint32_t finalVoltage_mV = 0;
    
    //Initialize GPIOs
    gpio_set_direction(GPIO_SYNC_SIG, GPIO_MODE_INPUT); // GPIO for state signaling
    gpio_set_pull_mode(GPIO_SYNC_SIG, GPIO_PULLDOWN_ONLY);

    gpio_set_direction(GPIO_CHARGE, GPIO_MODE_OUTPUT);
    gpio_set_direction(GPIO_POWER_ON, GPIO_MODE_OUTPUT);

    int64_t startTime = esp_timer_get_time();
    for(int i = 0 ; i <100; i++)
    {
    // Charge Caps
    ESP_LOGI(TAG, "Measurement %i - Charging Caps...", i);
    gpio_set_level(GPIO_POWER_ON,0);
    gpio_set_level(GPIO_CHARGE,1);
    vTaskDelay(chargingTime_ms);
    gpio_set_level(GPIO_CHARGE,0);

    // Power ESP on
    gpio_set_level(GPIO_POWER_ON,1);

    ESP_LOGD(TAG, "Waiting for boot up...");
    while(true)
    {
        if(1 == gpio_get_level(GPIO_SYNC_SIG))
        {
            break;
        }
    }
        energyunit_measureVoltage();
    
        //TODO: Measure at vdrop as rebounce.
       // Wait for start signal  
        
        ESP_LOGD(TAG, "Waiting for signal...");
        while(true)
        {
            if(0 == gpio_get_level(GPIO_SYNC_SIG))
            {
                break;
            }
        }
        startVoltage_mV = energyunit_measureVoltage();
        ESP_LOGD(TAG, "Initial Voltage: %lu mV",  startVoltage_mV); 
        
        prv_startSWTimer();
        
        while(0 == gpio_get_level(GPIO_SYNC_SIG));  
        
        xTimerStop(xTimer1,0);
        vTaskDelay(pdMS_TO_TICKS(25));
        finalVoltage_mV = energyunit_measureVoltage();
        int errCnt = 0;
        while(startVoltage_mV<finalVoltage_mV)
        {
            finalVoltage_mV = energyunit_measureVoltage();
            if(errCnt>10)
            {break;}
        }
        
        uint32_t voltageDrop_mV = 0;
        if(minVoltage_mV<=finalVoltage_mV && startVoltage_mV>=finalVoltage_mV) {
            voltageDrop_mV = finalVoltage_mV - minVoltage_mV;
            printf("Delta Voltage: %lu mV\n", startVoltage_mV-finalVoltage_mV); 
            printf("Voltage Drop: %lu mV\n", voltageDrop_mV); 
        }
        else if (finalVoltage_mV<minVoltage_mV)
        {
            ESP_LOGW(TAG, "Min Voltage: %lu final Voltage: %lu", minVoltage_mV, finalVoltage_mV); 
            i--;
        }
        else if (startVoltage_mV<finalVoltage_mV)
        {
            ESP_LOGW(TAG, "final Voltage: %lu", finalVoltage_mV); 
            i--;
        }
        
    }
    int64_t taskTime_us = esp_timer_get_time() - startTime;
    ESP_LOGI(TAG, "Measurement complete after: %lli s", taskTime_us/1000000); 
}


void prv_TimerCallbackFunction(TimerHandle_t pxTimer)
{
    ESP_LOGD(TAG,"MeasuringTime");
    uint32_t measuredVoltage_mV = energyunit_measureVoltage();
    if(measuredVoltage_mV<minVoltage_mV)
    {
        minVoltage_mV = measuredVoltage_mV;
    }
}

bool prv_createSWTimer(void)
{
    bool timerCreated = false;
    xTimer1 = xTimerCreate("Timer 1",     // Just a text name, not used by the kernel.
                tt_Delay_ms,    // The timer period in ticks.
                pdTRUE,        // The timer will auto-reload themselves when they expire.
                ( void * ) 0,           // Timer identifier.
               prv_TimerCallbackFunction); // Callback function
    
    if( xTimer1 == NULL )
    {
        ESP_LOGE(TAG,"Timer was not created!");
    }
    else
    {
        timerCreated = true;
    }
    return timerCreated;
}

bool prv_startSWTimer(void)
{
    bool timerOK = false; 
    if( xTimerStart( xTimer1, 0 ) != pdPASS )
    {
        ESP_LOGE(TAG,"The timer could not be set into the Active state.");
    }
    else
    {
        ESP_LOGD(TAG,"The timer was set into Active state.");
        timerOK = true; 
    }
    return timerOK;
}