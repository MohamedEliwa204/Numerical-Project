export interface RequestData {
    A : string[][],
    b : string[],
    method : string,
    precision : number,
    withScaling : boolean,
    initial_guess? : string[],
    num_of_ites? : number,
    abs_rel_error? : number
}
