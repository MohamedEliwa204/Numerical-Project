export interface ResponseData {
    solution : (number | string)[],
    executionTime : number,
    num_of_ites? : number,
    steps : SimulationStep[],
    steps_descriptions : string[],
    Xs_steps : string[],
    Ys_steps : string[]
}
