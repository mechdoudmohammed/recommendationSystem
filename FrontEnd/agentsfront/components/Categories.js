import { useEffect, useState } from "react";
import axios from "axios";
import React, { useRef } from 'react';

const Categories = () => {

    const [data, setData] = useState([])
    useEffect(() => {
        // Your side effect code here
        async function getdata() {
            try {
                const categories = await axios.get("http://127.0.0.1:8000/categories");

                setData(categories.data)
                console.log(categories.data);
            } catch (error) {
                console.error("Error fetching products:", error);
            }
        }
        getdata()
    }, []);


    const scrollRef = useRef(null);

    // Function to scroll right
    const scrollRight = () => {
        scrollRef.current.scrollBy({ left: 300, behavior: 'smooth' });
    };

    // Function to scroll left
    const scrollLeft = () => {
        scrollRef.current.scrollBy({ left: -300, behavior: 'smooth' });
    };

    return (
        <>
            {/* <div className=" bg-white  w-full ">


            <div className="flex py-5  mx-20 ">

                <div className=" overflow-x-scroll hide-scroll-bar no-scrollbar flex  space-x-4   md:w-full  xl:shadow-small-blue">
                    {data ? (
                        data.map(categorie => (
                            <a href="#" class="block  py-10 text-center ">
                                <div>
                                    <img src= {`http://localhost:8000${categorie.img_path}`} className="block mx-auto w-[30px] " />

                                    <p class="pt-4 text-sm font-medium capitalize font-body text-gray-900 lg:text-lg md:text-base md:pt-6">
                                        {categorie?.name}
                                    </p>
                                </div>
                            </a>))



                    ) : (
                        <div>Loading...</div>
                    )}



                </div>

            </div>

        </div> */}


            <div className="relative w-full py-6  bg-white ">
                {/* Scroll Buttons */}
                <button
                    onClick={scrollLeft}
                    className="absolute left-10 top-1/2 items-center justify-center drop-shadow-md transform -translate-y-1/2 bg-gray-100 p-4 rounded-full shadow-md"
                >
                    <img src="icons/rarrow.png" className="w-4 h-4 rotate-180" />
                </button>

                <button
                    onClick={scrollRight}
                    className="absolute items-center justify-center right-10 top-1/2 transform drop-shadow-md -translate-y-1/2 bg-gray-100 p-4 rounded-full shadow-md"
                >
                    <img src="icons/rarrow.png" className="w-4 h-4 " />
                </button>

                {/* Scrollable Container */}
                <div className="mx-20">
                <div
                    ref={scrollRef}
                    className="overflow-x-scroll hide-scroll-bar no-scrollbar flex  space-x-4    md:w-full  xl:shadow-small-blue"
                >
                    {data.map((categorie, index) => (
                        <div key={index} className="f">
                            <a href="#" class="block border-2 w-[135px] h-[135px] p-4 rounded-full space-y-1  py-10 text-center ">
                                
                                    <img src={`http://localhost:8000${categorie.img_path}`} className="block mx-auto w-[30px] " />

                                    <p class=" text-sm font-medium capitalize font-body text-gray-900 lg:text-sm  md:text-base ">
                                        {categorie?.name}
                                    </p>
                                
                            </a>
                        </div>
                    ))}
                </div>
                </div>
            </div>
        </>
    )
}
export default Categories;