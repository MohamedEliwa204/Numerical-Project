export interface RequestData {
    A : number[][],
    b : number[],
    method : string,
    precision : number,
    withScaling : boolean,
    initial_guess? : number[],
    num_of_ites? : number,
    abs_rel_error? : number
}
