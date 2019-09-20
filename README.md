# Firmware

This repository contains all the code to control the ROV from the companion computer.

See the [Communication18-19](https://github.com/CWRUbotixROV/Communication/tree/Communication18-19)
branch for last year's code.

## General Directory Structure

- root
    - Communication
        - **Note:** contains all the code to communicate with the surface computer.
            - ie the program that handles processing the packets that are sent from the surface and tell the Pi to perform some action.
            - Note that these actions are telling the sensors or other peripherals on the robot to do something.  This does not govern the mavlink messages used to control the robot's general movement, but would involve moving a servo for a specific task.
    - Documentation
        - **Note:** Any reference materials that would be useful for using something in this repository.  These should likely be Markdown files unless there's a good reason not to do that.
        - Resources
            - **Note:** this folder should contain images or other resources linked by the documents at the root of the Documentation folder.
            - Images
    - Peripherals
        - **Note:** each sensor, motor, servo, or other peripheral should have its own folder to represent the module
        - Sensors
        - Motors

